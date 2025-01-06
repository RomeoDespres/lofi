from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select

from lofi import db
from lofi.etl.main import get_new_lofi_tracklist
from tests.utils import (
    AlbumGenerator,
    LabelGenerator,
    PlaylistGenerator,
    TrackGenerator,
    TrackPopularityGenerator,
    iterator_to_list,
    load_data_output,
)

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture
@load_data_output
@iterator_to_list
def playlists(session: db.Session, playlist_generator: PlaylistGenerator) -> Iterator[db.Playlist]:  # noqa: ARG001
    for _ in range(2):
        yield playlist_generator.generate()


@pytest.fixture
@load_data_output
def lofi_label(session: db.Session, playlists: list[db.Playlist], label_generator: LabelGenerator) -> db.Label:  # noqa: ARG001
    return label_generator.generate(is_lofi=True, playlist_id=playlists[0].id, playlist=playlists[0])


@pytest.fixture
@load_data_output
def non_lofi_label(session: db.Session, playlists: list[db.Playlist], label_generator: LabelGenerator) -> db.Label:  # noqa: ARG001
    return label_generator.generate(is_lofi=False, playlist_id=playlists[1].id, playlist=playlists[1])


@pytest.fixture
def labels(lofi_label: db.Label, non_lofi_label: db.Label) -> list[db.Label]:
    return [lofi_label, non_lofi_label]


@pytest.fixture
@load_data_output
def new_album(session: db.Session, lofi_label: db.Label, album_generator: AlbumGenerator) -> db.Album:  # noqa: ARG001
    return album_generator.generate(label=lofi_label, label_name=lofi_label.name, release_date=datetime.date.today())


@pytest.fixture
@load_data_output
def non_lofi_album(session: db.Session, non_lofi_label: db.Label, album_generator: AlbumGenerator) -> db.Album:  # noqa: ARG001
    return album_generator.generate(
        label=non_lofi_label,
        label_name=non_lofi_label.name,
        release_date=datetime.date.today(),
    )


@pytest.fixture
@load_data_output
def old_album(session: db.Session, lofi_label: db.Label, album_generator: AlbumGenerator) -> db.Album:  # noqa: ARG001
    return album_generator.generate(
        label=lofi_label,
        label_name=lofi_label.name,
        release_date=datetime.date.today() - datetime.timedelta(days=365),
    )


@pytest.fixture
def albums(new_album: db.Album, non_lofi_album: db.Album, old_album: db.Album) -> list[db.Album]:
    return [new_album, non_lofi_album, old_album]


@pytest.fixture
@load_data_output
@iterator_to_list
def tracks(session: db.Session, albums: list[db.Album], track_generator: TrackGenerator) -> Iterator[db.Track]:  # noqa: ARG001
    for i, album in zip(range(5), albums):
        yield track_generator.generate(album_id=album.id, album=album, position=i)


@pytest.fixture
@load_data_output
@iterator_to_list
def track_popularities(
    session: db.Session,  # noqa: ARG001
    tracks: list[db.Track],
    track_popularity_generator: TrackPopularityGenerator,
) -> Iterator[db.TrackPopularity]:
    for track in tracks:
        yield track_popularity_generator.generate(track_id=track.id, track=track)


@pytest.fixture
def new_lofi_tracklist(session: db.Session, track_popularities: list[db.TrackPopularity]) -> list[db.Track]:  # noqa: ARG001
    ids = get_new_lofi_tracklist(session)
    tracks = list(session.execute(select(db.Track).where(db.Track.id.in_(ids))).scalars())
    assert len(tracks) == len(ids)
    return tracks


def test_get_new_lofi_tracklist_is_not_empty(new_lofi_tracklist: list[db.Track]) -> None:
    assert len(new_lofi_tracklist) > 0


def test_get_new_lofi_tracklist_only_returns_lofi_labels(
    lofi_label: db.Label,
    new_lofi_tracklist: list[db.Track],
) -> None:
    for track in new_lofi_tracklist:
        assert track.album.label_name == lofi_label.name


def test_get_new_lofi_tracklist_returns_recent_tracks(new_album: db.Album, new_lofi_tracklist: list[db.Track]) -> None:
    for track in new_lofi_tracklist:
        assert track.album.id == new_album.id


def test_get_new_lofi_tracklist_returns_all_recent_tracks(
    session: db.Session,
    new_album: db.Album,
    new_lofi_tracklist: list[db.Track],
) -> None:
    new_album_bound = session.get(db.Album, new_album.id)
    assert new_album_bound is not None
    ids = {track.id for track in new_lofi_tracklist}
    assert ids == {track.id for track in new_album_bound.tracks}


def test_get_new_lofi_tracklist_is_ordered_by_decreasing_popularity(new_lofi_tracklist: list[db.Track]) -> None:
    popularities = [track.popularity[-1].popularity for track in new_lofi_tracklist]
    assert popularities == sorted(popularities, reverse=True)
