from __future__ import annotations

import datetime
from collections.abc import Sequence  # noqa: TC003
from typing import Generic, TypeVar

from pydantic import BaseModel, field_validator

from lofi import db  # noqa: TC001

_T = TypeVar("_T")


def parse_date(s: str) -> datetime.date:
    return datetime.datetime.strptime(f"{s}-01-01"[:10], "%Y-%m-%d").date()  # noqa: DTZ007


class HasIdAndName(BaseModel):
    id: str
    name: str


class User(BaseModel):
    id: str
    display_name: str


class PlaylistTrack(BaseModel):
    id: str


class ImageUrl(BaseModel):
    height: int | None
    url: str
    width: int | None


class Playlist(HasIdAndName):
    images: list[ImageUrl]
    owner: User
    snapshot_id: str


class TrackAlbum(HasIdAndName):
    pass


class TrackArtist(HasIdAndName):
    pass


class TrackExternalIds(BaseModel):
    isrc: str


class Track(HasIdAndName):
    album: TrackAlbum
    artists: Sequence[TrackArtist]
    external_ids: TrackExternalIds
    popularity: int
    track_number: int


class SearchAlbumArtist(HasIdAndName):
    pass


class SearchAlbum(HasIdAndName):
    album_type: db.AlbumType
    artists: Sequence[SearchAlbumArtist]
    release_date: datetime.date

    @field_validator("release_date", mode="before")
    @classmethod
    def parse_release_date(cls, d: str) -> datetime.date:
        return parse_date(d)


class Items(BaseModel, Generic[_T]):
    items: Sequence[_T]


class AlbumTrack(HasIdAndName):
    pass


class Album(SearchAlbum):
    label: str
    popularity: int
    tracks: Items[AlbumTrack]


class ArtistAlbum(HasIdAndName):
    release_date: datetime.date
    total_tracks: int

    @field_validator("release_date", mode="before")
    @classmethod
    def parse_release_date(cls, d: str) -> datetime.date:
        return parse_date(d)
