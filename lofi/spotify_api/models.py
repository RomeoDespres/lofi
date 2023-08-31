import datetime
from typing import Generic, Sequence, TypeVar

from pydantic import BaseModel, field_validator

from .. import db


_T = TypeVar("_T")


def parse_date(s: str) -> datetime.date:
    return datetime.datetime.strptime(f"{s}-01-01"[:10], "%Y-%m-%d").date()


class HasIdAndName(BaseModel):
    id: str
    name: str


class User(BaseModel):
    id: str
    display_name: str


class PlaylistTrack(BaseModel):
    id: str


class Playlist(HasIdAndName):
    owner: User


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
    pass
