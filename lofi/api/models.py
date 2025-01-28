from __future__ import annotations

import datetime  # noqa: TC003

import pydantic
from humps import camelize

from lofi import db  # noqa: TC001


class BaseModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        alias_generator=camelize,
        from_attributes=True,
        json_schema_serialization_defaults_required=True,
        populate_by_name=True,
    )


class ArtistTrackArtist(BaseModel):
    id: str
    image_url_s: str | None
    name: str


class BasicLabelPlaylist(BaseModel):
    image_url: str


class BasicLabel(BaseModel):
    name: str
    playlist: BasicLabelPlaylist


class ArtistTrackAlbum(BaseModel):
    artists: list[ArtistTrackArtist]
    id: str
    image_url_s: str | None
    label: BasicLabel
    name: str
    release_date: datetime.date
    type: db.AlbumType


class ArtistTrack(BaseModel):
    album: ArtistTrackAlbum
    artists: list[ArtistTrackArtist]
    id: str
    isrc: str
    name: str


class Artist(BaseModel):
    name: str
    id: str
    image_url_l: str | None
    tracks: list[ArtistTrack]


class ArtistIndexEntry(BaseModel):
    name: str
    id: str
    image_url_s: str | None = None


class ArtistIndex(BaseModel):
    artists: list[ArtistIndexEntry]


class StreamsRange(BaseModel):
    max: int
    min: int


class Label(BaseModel):
    image_url: str
    name: str
    popularity: float
    playlist_id: str
    tracks: int
    tracks_in_editorials: int
    streams: StreamsRange


class Labels(BaseModel):
    labels: list[Label]
