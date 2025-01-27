from __future__ import annotations

import functools
import itertools
import operator
import time
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Concatenate,
    ParamSpec,
    TypeVar,
    cast,
)

import spotipy  # type: ignore[import-untyped]
from requests import ConnectionError as RequestsConnectionError
from requests import ReadTimeout
from spotipy.oauth2 import SpotifyOAuth  # type: ignore[import-untyped]
from tqdm import tqdm

from lofi import db, env

from .cache_handler import CacheHandler
from .errors import PlaylistAlreadyExistsError
from .log import LOGGER
from .models import (
    Album,
    Artist,
    ArtistAlbum,
    Playlist,
    PlaylistTrack,
    SearchAlbum,
    Track,
    User,
)
from .tracklist_utils import get_tracklist_reorders

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

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
    l1: Sequence[_T],
    l2: Sequence[_T],
) -> tuple[list[_T], list[_T]]:
    l1, l2 = list(l1), list(l2)
    i = get_first_differing_index(reversed(l1), reversed(l2))
    if i is not None:
        if i == 0:
            return l1, l2
        return l1[:-i], l2[:-i]
    if (n := len(l2) - len(l1)) > 0:
        return [], l2[:n]
    return l1[:-n], []


def retry_on_timeout(
    func: Callable[Concatenate[SpotifyAPIClient, _P], _T],
) -> Callable[Concatenate[SpotifyAPIClient, _P], _T]:
    @functools.wraps(func)
    def wrapped(self: SpotifyAPIClient, *args: _P.args, **kwargs: _P.kwargs) -> _T:
        max_retries = 10
        for i in range(11):
            try:
                return func(self, *args, **kwargs)
            except (ReadTimeout, RequestsConnectionError):  # noqa: PERF203
                if i == max_retries:
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
        response: Any,  # noqa: ANN401
        max_offset: int | None = None,
        subkey: str | None = None,
    ) -> list[dict[str, Any]]:
        def get_subkey(response: Any) -> Any:  # noqa: ANN401
            return response if subkey is None else response[subkey]

        response = get_subkey(response)
        items: list[dict[str, Any] | None] = response["items"]
        while response.get("next") and (max_offset is None or response.get("offset", max_offset) < max_offset):
            response = get_subkey(self.api.next(response))
            items.extend(response["items"])
        return [item for item in items if item is not None]

    @retry_on_timeout
    def albums(self, ids: Sequence[str], *, with_all_tracks: bool = False) -> list[Album]:
        albums: list[Any] = []
        for i in tqdm(range(0, len(ids), 20), unit_scale=20):
            albums.extend(
                [a for a in self.api.albums(ids[i : i + 20])["albums"] if a is not None],
            )
            if not with_all_tracks:
                continue
            for album in albums[i : i + 20]:
                album["tracks"]["items"] = self._get_items(album["tracks"])

        return list(map(Album.model_validate, albums))

    @retry_on_timeout
    def artist_albums(self, artist_id: str) -> list[ArtistAlbum]:
        items = self.api.artist_albums(artist_id, country="US", limit=50)
        return list(map(ArtistAlbum.model_validate, self._get_items(items)))

    @retry_on_timeout
    def artists(self, ids: Sequence[str]) -> list[Artist]:
        artists: list[Any] = []
        for i in tqdm(range(0, len(ids), 50), unit_scale=50):
            artists.extend(
                [a for a in self.api.artists(ids[i : i + 50])["artists"] if a is not None],
            )

        return list(map(Artist.model_validate, artists))

    @retry_on_timeout
    def create_playlist(
        self,
        name: str,
        description: str = "",
        *,
        public: bool = True,
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
        resp = self.api.user_playlist_create(self.user_id, name, public=public, description=description)
        return Playlist.model_validate(resp)

    @retry_on_timeout
    def me(self) -> User:
        LOGGER.info("Getting current Spotify user information")
        return User.model_validate(self.api.me())

    @retry_on_timeout
    def playlist(self, playlist_id: str) -> Playlist:
        return Playlist.model_validate(self.api.playlist(playlist_id))

    @retry_on_timeout
    def playlist_tracks(self, playlist_id: str) -> list[PlaylistTrack]:
        LOGGER.info(f"Fetching tracks of Spotify playlist {playlist_id}")
        items = self._get_items(self.api.playlist_items(playlist_id, limit=100))
        raw_tracks = [item["track"] for item in items if item["track"] is not None]
        return list(map(PlaylistTrack.model_validate, raw_tracks))

    @retry_on_timeout
    def search_albums(self, q: str) -> list[SearchAlbum]:
        LOGGER.info(f"Searching for {q=}")
        items = self._get_items(self.api.search(q, type="album", limit=50), 950, "albums")
        return list(map(SearchAlbum.model_validate, items))

    @retry_on_timeout
    def set_playlist_tracks(
        self,
        playlist_id: str,
        ids: Sequence[str],
        current_ids: Sequence[str] | None = None,
        *,
        use_reorders: bool = False,
    ) -> None:
        LOGGER.info(f"Updating tracklist of Spotify playlist {playlist_id}")
        if current_ids is None:
            current_ids = [track.id for track in self.playlist_tracks(playlist_id)]
        else:
            LOGGER.info("Current snapshot already in database")
            current_ids = list(current_ids)
        if ids == current_ids:
            LOGGER.info("Playlist already has required tracklist")
            return
        current_ids_set = set(current_ids)
        ids_to_remove_set = current_ids_set - set(ids)
        if use_reorders:
            ids_to_add = [track_id for track_id in ids if track_id not in current_ids_set]
            ids_to_remove = list(ids_to_remove_set)
        else:
            ids_to_add, ids_to_remove = get_tracklist_diffs(ids, current_ids)
        LOGGER.info(f"Removing {len(ids_to_remove):,} tracks")
        for ids_chunk in chunk(ids_to_remove, 100):
            self.api.playlist_remove_all_occurrences_of_items(playlist_id, ids_chunk)
        LOGGER.info(f"Adding {len(ids_to_add):,} tracks")
        for i, ids_chunk in enumerate(chunk(ids_to_add, 100)):
            self.api.playlist_add_items(playlist_id, ids_chunk, position=i * 100)
        if use_reorders:
            current_ids = ids_to_add + [track_id for track_id in current_ids if track_id not in ids_to_remove_set]
            for reorder in get_tracklist_reorders(ids, current_ids):
                self.api.playlist_reorder_items(
                    playlist_id,
                    reorder.range_start,
                    reorder.insert_before,
                    reorder.range_length,
                )

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
