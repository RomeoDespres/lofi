from __future__ import annotations

import functools
import itertools
import operator
import time
from typing import (
    Any,
    Callable,
    Concatenate,
    Iterable,
    ParamSpec,
    Sequence,
    TypeVar,
    cast,
)

from requests import ConnectionError, ReadTimeout
import spotipy  # type: ignore
from spotipy.oauth2 import SpotifyOAuth  # type: ignore
from tqdm import tqdm

from .. import db
from .. import env
from .cache_handler import CacheHandler
from .errors import PlaylistAlreadyExistsError
from .log import LOGGER
from .models import Album, Playlist, PlaylistTrack, SearchAlbum, Track, User


_T = TypeVar("_T")
_P = ParamSpec("_P")


def chunk(it: Sequence[_T], size: int) -> Iterable[Sequence[_T]]:
    for i in range(0, len(it), size):
        yield it[i : i + size]


def get_first_differing_index(l1: Iterable[Any], l2: Iterable[Any]) -> int | None:
    try:
        return next(itertools.compress(itertools.count(), map(operator.ne, l1, l2)))
    except StopIteration:
        return None


def get_tracklist_diffs(
    l1: Sequence[_T], l2: Sequence[_T]
) -> tuple[Sequence[_T], Sequence[_T]]:
    i = get_first_differing_index(reversed(l1), reversed(l2))
    if i is not None:
        if i == 0:
            return l1, l2
        return l1[:-i], l2[:-i]
    if (n := len(l2) - len(l1)) > 0:
        return [], l2[:n]
    return l1[:-n], []


def retry_on_timeout(
    func: Callable[Concatenate[SpotifyAPIClient, _P], _T]
) -> Callable[Concatenate[SpotifyAPIClient, _P], _T]:
    @functools.wraps(func)
    def wrapped(self: SpotifyAPIClient, *args: _P.args, **kwargs: _P.kwargs) -> _T:
        for i in range(11):
            try:
                return func(self, *args, **kwargs)
            except (ReadTimeout, ConnectionError):
                if i == 10:
                    raise
                n = 2**i
                LOGGER.warning(f"Spotify API error. Retrying in {n} seconds")
                time.sleep(n)
                self.api = self.get_api(self.session)

        # Following code is unreachable, only here for type check
        raise NotImplementedError  # pragma: no cover

    return cast(Callable[Concatenate["SpotifyAPIClient", _P], _T], wrapped)


class SpotifyAPIClient:
    def __init__(self, session: db.Session, user_id: str | None = None) -> None:
        self.user_id = env.spotify_user_id() if user_id is None else user_id
        self.api = self.get_api(session)
        self.session = session

    def get_api(self, session: db.Session) -> spotipy.Spotify:
        """Return spotipy API client."""
        scopes = (
            "playlist-modify-public",
            "playlist-modify-private",
            "playlist-read-private",
            "playlist-read-collaborative",
        )
        return spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                cache_handler=CacheHandler(user_id=self.user_id, session=session),
                scope=",".join(scopes),
            ),
            requests_timeout=60,
            retries=10,
        )

    def _get_items(
        self,
        response: Any,
        max_offset: int | None = None,
        subkey: str | None = None,
    ) -> list[dict[str, Any]]:
        def get_subkey(response: Any) -> Any:
            return response if subkey is None else response[subkey]

        response = get_subkey(response)
        items: list[dict[str, Any]] = response["items"]
        while response.get("next") and (
            max_offset is None or response.get("offset", max_offset) < max_offset
        ):
            response = get_subkey(self.api.next(response))
            items.extend(response["items"])
        return items

    @retry_on_timeout
    def albums(self, ids: Sequence[str], with_all_tracks: bool = False) -> list[Album]:
        albums: list[Any] = []
        for i in tqdm(range(0, len(ids), 20), unit_scale=20):
            albums.extend(
                [a for a in self.api.albums(ids[i : i + 20])["albums"] if a is not None]
            )
            if not with_all_tracks:
                continue
            for album in albums[i : i + 20]:
                album["tracks"]["items"] = self._get_items(album["tracks"])

        return list(map(Album.model_validate, albums))

    @retry_on_timeout
    def create_playlist(
        self,
        name: str,
        description: str = "",
        public: bool = True,
        *,
        allow_duplicates: bool = False,
        skip_if_already_exists: bool = False,
    ) -> Playlist:
        LOGGER.info(f"Creating Spotify playlist with {name=}")
        playlists = self.user_playlists(self.user_id)
        matching = [p for p in playlists if p.name == name]
        if matching and not allow_duplicates:
            if skip_if_already_exists:
                LOGGER.info("Playlist already exists, skipping")
                return matching[0]
            raise PlaylistAlreadyExistsError(self.user_id, name, matching[0].id)
        resp = self.api.user_playlist_create(
            self.user_id, name, public=public, description=description
        )
        return Playlist.model_validate(resp)

    @retry_on_timeout
    def me(self) -> User:
        LOGGER.info("Getting current Spotify user information")
        return User.model_validate(self.api.me())

    @retry_on_timeout
    def playlist_tracks(self, id: str) -> list[PlaylistTrack]:
        LOGGER.info(f"Fetching tracks of Spotify playlist {id}")
        items = self._get_items(self.api.playlist_items(id, limit=100))
        raw_tracks = [item["track"] for item in items]
        return list(map(PlaylistTrack.model_validate, raw_tracks))

    @retry_on_timeout
    def search_albums(self, q: str) -> list[SearchAlbum]:
        LOGGER.info(f"Searching for {q=}")
        items = self._get_items(
            (s := self.api.search(q, type="album", limit=50, market="FR")),
            950,
            "albums",
        )
        print(s)
        return list(map(SearchAlbum.model_validate, items))

    @retry_on_timeout
    def set_playlist_tracks(
        self, id: str, ids: Sequence[str], current_ids: Sequence[str] | None = None
    ) -> None:
        LOGGER.info(f"Updating tracklist of Spotify playlist {id}")
        if current_ids is None:
            current_ids = [track.id for track in self.playlist_tracks(id)]
        else:
            LOGGER.info("Current snapshot already in database")
        ids_to_add, ids_to_remove = get_tracklist_diffs(ids, current_ids)
        LOGGER.info(f"Removing {len(ids_to_remove):,} tracks")
        for ids_chunk in chunk(ids_to_remove, 100):
            self.api.playlist_remove_all_occurrences_of_items(id, ids_chunk)
        LOGGER.info(f"Adding {len(ids_to_add):,} tracks")
        for i, ids_chunk in enumerate(chunk(ids_to_add, 100)):
            self.api.playlist_add_items(id, ids_chunk, position=i * 100)

    @retry_on_timeout
    def snapshot_id(self, playlist_id: str) -> str:
        """Return current snapshot ID of a playlist."""
        return str(self.api.playlist(playlist_id)["snapshot_id"])

    @retry_on_timeout
    def tracks(self, ids: Sequence[str]) -> list[Track]:
        n = 50
        tracks = (
            t
            for i in tqdm(range(0, len(ids), n), unit_scale=n)
            for t in self.api.tracks(ids[i : i + n])["tracks"]
            if t is not None
        )
        return list(map(Track.model_validate, tracks))

    @retry_on_timeout
    def user_playlists(self, user_id: str) -> list[Playlist]:
        LOGGER.info(f"Fetching playlists for user {user_id} from Spotify")
        items = self._get_items(self.api.user_playlists(user_id))
        return list(map(Playlist.model_validate, items))
