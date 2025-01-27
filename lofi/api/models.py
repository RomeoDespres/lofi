from __future__ import annotations

import pydantic
from humps import camelize


class BaseModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        alias_generator=camelize,
        from_attributes=True,
        json_schema_serialization_defaults_required=True,
        populate_by_name=True,
    )


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
