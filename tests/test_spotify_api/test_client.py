import time
from typing import Any, Sequence, Type
from unittest.mock import patch

import pytest
from requests import ConnectionError, ReadTimeout

from lofi import db
from lofi.spotify_api import SpotifyAPIClient
from lofi.spotify_api.client import (
    chunk,
    get_first_differing_index,
    get_tracklist_diffs,
    retry_on_timeout,
)
from lofi.spotify_api.models import User


@pytest.fixture
def default_user_id(monkeypatch: pytest.MonkeyPatch) -> str:
    monkeypatch.setenv("SPOTIFY_USER_ID", user_id := "foo")
    return user_id


def get_patched_client(session: db.Session, **kwargs: Any) -> SpotifyAPIClient:
    client = SpotifyAPIClient(session)
    for key, value in kwargs.items():
        setattr(client.api, key, value)
    return client


def test_client_uses_env_variable_if_no_user_id_is_provided(
    session: db.Session, default_user_id: str
) -> None:
    assert SpotifyAPIClient(session).user_id == default_user_id


@pytest.mark.parametrize(
    ["l1", "l2", "expected"],
    [
        ([], [], None),
        ([], [1, 2], None),
        ([1], [1, 2], None),
        ([1, 2, 3], [1, 2, 4], 2),
        ([1, 2], [1, 0, 3], 1),
    ],
)
def test_get_first_differing_index(l1: list[int], l2: list[int], expected: int) -> None:
    assert get_first_differing_index(l1, l2) == expected
    assert get_first_differing_index(l2, l1) == expected


@pytest.mark.parametrize(
    ["target", "current", "expected_added", "expected_removed"],
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
def test_retry_on_timeout(
    session: db.Session, exc: Type[ConnectionError | ReadTimeout]
) -> None:
    with patch.object(time, "sleep") as mock:

        @retry_on_timeout
        def raise_exc(self: SpotifyAPIClient) -> None:
            raise exc()

        with pytest.raises(exc):
            raise_exc(SpotifyAPIClient(session))

    call_args = [call.args for call in mock.call_args_list]
    assert call_args == [(2**i,) for i in range(10)]


@pytest.mark.parametrize(
    ["it", "n", "expected"],
    [
        ([], 2, []),
        (range(5), 2, [[0, 1], [2, 3], [4]]),
    ],
)
def test_chunk(it: Sequence[int], n: int, expected: list[list[int]]) -> None:
    chunks = list(map(lambda c: list(c), chunk(it, n)))
    assert chunks == expected


def test_me(session: db.Session, default_user_id: str) -> None:
    data = {"id": default_user_id, "display_name": "foo"}
    expected = User.model_validate(data)
    api = get_patched_client(session, me=lambda: data)
    assert api.me() == expected


@pytest.mark.usefixtures("default_user_id")
@pytest.mark.parametrize("fetch_current_tracklist", [True, False])
def test_set_playlist_tracks(
    session: db.Session, fetch_current_tracklist: bool
) -> None:
    playlist_id = "foo"
    playlists: dict[str, list[str]] = {
        playlist_id: list(map(str, reversed(range(10, 1000, 3))))
    }

    def add_items(id: str, ids: list[str], position: int) -> None:
        playlists[id] = playlists[id][:position] + ids + playlists[id][position:]

    def remove_items(id: str, ids: list[str]) -> None:
        ids_set = set(ids)
        playlists[id] = [t for t in playlists[id] if t not in ids_set]

    def get_items(id: str, limit: int, offset: int = 0) -> dict[str, Any]:
        return {
            "id": id,
            "items": [
                {"track": {"id": track_id}}
                for track_id in playlists[id][offset : offset + limit]
            ],
            "offset": offset,
            "limit": limit,
            "next": None if offset + limit >= len(playlists[id]) else True,
        }

    def next(resp: Any) -> Any:
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
    api = get_patched_client(session, playlist=lambda id: {"snapshot_id": snapshot_id})
    assert api.snapshot_id("") == snapshot_id
