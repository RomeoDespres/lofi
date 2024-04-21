from __future__ import annotations

import datetime
import time
from typing import TYPE_CHECKING, Any, Sequence
from unittest.mock import Mock, patch

import pytest
from requests import ConnectionError, ReadTimeout

from lofi.spotify_api import SpotifyAPIClient
from lofi.spotify_api.client import chunk, get_first_differing_index, get_tracklist_diffs, retry_on_timeout
from lofi.spotify_api.errors import PlaylistAlreadyExistsError
from lofi.spotify_api.models import ArtistAlbum, Playlist, User

if TYPE_CHECKING:
    from lofi import db

DEFAULT_PATCHED_PLAYLIST = {
    "id": "",
    "images": [],
    "name": "",
    "owner": {"id": "", "display_name": ""},
    "snapshot_id": "",
}


@pytest.fixture()
def default_user_id(monkeypatch: pytest.MonkeyPatch) -> str:
    monkeypatch.setenv("SPOTIFY_USER_ID", user_id := "foo")
    return user_id


def get_patched_client(session: db.Session, **kwargs: object) -> SpotifyAPIClient:
    client = SpotifyAPIClient(session)
    for key, value in kwargs.items():
        setattr(client.api, key, value)
    return client


def test_client_uses_env_variable_if_no_user_id_is_provided(session: db.Session, default_user_id: str) -> None:
    assert SpotifyAPIClient(session).user_id == default_user_id


@pytest.mark.parametrize(
    ("l1", "l2", "expected"),
    [([], [], None), ([], [1, 2], None), ([1], [1, 2], None), ([1, 2, 3], [1, 2, 4], 2), ([1, 2], [1, 0, 3], 1)],
)
def test_get_first_differing_index(l1: list[int], l2: list[int], expected: int) -> None:
    assert get_first_differing_index(l1, l2) == expected
    assert get_first_differing_index(l2, l1) == expected


@pytest.mark.parametrize(
    ("target", "current", "expected_added", "expected_removed"),
    [
        ([], [], [], []),
        ([], [1, 2], [], [1, 2]),
        ([1], [1, 2], [1], [1, 2]),
        ([1, 2, 3], [2, 3], [1], []),
        ([1, 3], [1, 0, 3], [1], [1, 0]),
    ],
)
def test_get_tracklist_diffs(
    target: list[int],
    current: list[int],
    expected_added: list[int],
    expected_removed: list[int],
) -> None:
    assert get_tracklist_diffs(target, current) == (expected_added, expected_removed)


@pytest.mark.usefixtures("default_user_id")
@pytest.mark.parametrize("exc", [ConnectionError, ReadTimeout])
def test_retry_on_timeout(session: db.Session, exc: type[ConnectionError | ReadTimeout]) -> None:
    with patch.object(time, "sleep") as mock:

        @retry_on_timeout
        def raise_exc(self: SpotifyAPIClient) -> None:  # noqa: ARG001
            raise exc()

        with pytest.raises(exc):
            raise_exc(SpotifyAPIClient(session))

    call_args = [call.args for call in mock.call_args_list]
    assert call_args == [(2**i,) for i in range(10)]


@pytest.mark.parametrize(("it", "n", "expected"), [([], 2, []), (range(5), 2, [[0, 1], [2, 3], [4]])])
def test_chunk(it: Sequence[int], n: int, expected: list[list[int]]) -> None:
    chunks = [list(c) for c in chunk(it, n)]
    assert chunks == expected


def test_me(session: db.Session, default_user_id: str) -> None:
    data = {"id": default_user_id, "display_name": "foo"}
    expected = User.model_validate(data)
    api = get_patched_client(session, me=lambda: data)
    assert api.me() == expected


@pytest.mark.usefixtures("default_user_id")
@pytest.mark.parametrize("fetch_current_tracklist", [True, False])
def test_set_playlist_tracks(session: db.Session, *, fetch_current_tracklist: bool) -> None:
    playlist_id = "foo"
    playlists: dict[str, list[str]] = {
        playlist_id: list(map(str, reversed(range(10, 1000, 3)))),
    }

    def add_items(playlist_id: str, ids: list[str], position: int) -> None:
        playlists[playlist_id] = playlists[playlist_id][:position] + ids + playlists[playlist_id][position:]

    def remove_items(playlist_id: str, ids: list[str]) -> None:
        ids_set = set(ids)
        playlists[playlist_id] = [t for t in playlists[playlist_id] if t not in ids_set]

    def get_items(playlist_id: str, limit: int, offset: int = 0) -> dict[str, Any]:
        return {
            "id": playlist_id,
            "items": [{"track": {"id": track_id}} for track_id in playlists[playlist_id][offset : offset + limit]],
            "offset": offset,
            "limit": limit,
            "next": None if offset + limit >= len(playlists[playlist_id]) else True,
        }

    def next(resp: Any) -> object:  # noqa: A001, ANN401
        return get_items(resp["id"], resp["limit"], resp["offset"] + resp["limit"])

    api = get_patched_client(
        session,
        playlist_add_items=add_items,
        playlist_remove_all_occurrences_of_items=remove_items,
        playlist_items=get_items,
        next=next,
    )
    api.set_playlist_tracks(
        playlist_id,
        expected := list(map(str, reversed(range(1000)))),
        None if fetch_current_tracklist else playlists[playlist_id],
    )
    assert playlists[playlist_id] == expected


@pytest.mark.usefixtures("default_user_id")
def test_snapshot_id(session: db.Session) -> None:
    snapshot_id = "foo"
    patched_playlist = {**DEFAULT_PATCHED_PLAYLIST, "snapshot_id": snapshot_id}
    api = get_patched_client(session, playlist=lambda playlist_id: patched_playlist)  # noqa: ARG005
    assert api.playlist("").snapshot_id == snapshot_id


def test_create_playlist_that_already_exists_raises_error(session: db.Session, default_user_id: str) -> None:
    playlist = Playlist.model_validate(DEFAULT_PATCHED_PLAYLIST)
    api = get_patched_client(
        session,
        user_playlists=Mock(return_value={"items": [playlist.model_dump()]}),
    )
    with pytest.raises(PlaylistAlreadyExistsError) as exc_info:
        api.create_playlist(playlist.name)
    err = exc_info.value
    assert err.user_id == default_user_id
    assert err.playlist_id == playlist.id
    assert err.name == playlist.name


@pytest.mark.usefixtures("default_user_id")
def test_create_playlist_that_already_exists_returns_existing(session: db.Session) -> None:
    playlist = Playlist.model_validate(DEFAULT_PATCHED_PLAYLIST)
    api = get_patched_client(session, user_playlists=Mock(return_value={"items": [playlist.model_dump()]}))
    received = api.create_playlist(playlist.name, skip_if_already_exists=True)
    assert received == playlist


@pytest.mark.usefixtures("default_user_id")
def test_create_playlist_that_does_not_exist(session: db.Session) -> None:
    playlist = Playlist.model_validate(DEFAULT_PATCHED_PLAYLIST)
    create_playlist = Mock(return_value=playlist.model_dump())
    api = get_patched_client(
        session,
        user_playlists=Mock(return_value={"items": []}),
        user_playlist_create=create_playlist,
    )
    received = api.create_playlist(playlist.name)
    assert received == playlist
    create_playlist.assert_called_once()


@pytest.mark.usefixtures("default_user_id")
def test_get_artist_albums(session: db.Session) -> None:
    artist_id = "foo"
    props = {"release_date": datetime.date.today(), "total_tracks": 10}
    albums = [{"id": "foo", "name": "Foo", **props}, {"id": "bar", "name": "Bar", **props}]
    api = get_patched_client(session, artist_albums=Mock(return_value={"items": albums}))
    received = api.artist_albums(artist_id)
    assert received == list(map(ArtistAlbum.model_validate, albums))
