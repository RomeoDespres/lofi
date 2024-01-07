from humps import camelize
import pydantic


class BaseModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        alias_generator=camelize,
        from_attributes=True,
        json_schema_serialization_defaults_required=True,
        populate_by_name=True,
    )


class StreamsRange(BaseModel):
    max: int
    min: int


class Label(BaseModel):
    image_url: str
    name: str
    popularity: float
    playlist_id: str
    tracks: int
    streams: StreamsRange


class Labels(BaseModel):
    labels: list[Label]
