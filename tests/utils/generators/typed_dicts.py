import datetime
from typing import TypedDict

from lofi import db


class AlbumData(TypedDict):
    id: str
    label_name: str
    name: str
    release_date: datetime.date
    type: db.AlbumType


class LabelData(TypedDict):
    is_indie: bool
    is_lofi: bool
    name: str
    playlist_id: str


class PlaylistData(TypedDict):
    id: str
    image_url: str | None
    is_editorial: bool


class TrackData(TypedDict):
    id: str
    album_id: str
    isrc: str
    name: str
    position: int


class TrackPopularityData(TypedDict):
    track_id: str
    date: datetime.date
    popularity: int
