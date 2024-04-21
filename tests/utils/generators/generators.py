from lofi import db

from .data_generator import DataGenerator
from .typed_dicts import (
    AlbumData,
    LabelData,
    PlaylistData,
    TrackData,
    TrackPopularityData,
)


class AlbumGenerator(DataGenerator[AlbumData, db.Album]):
    def generate_default(self, id_: int) -> AlbumData:
        return {
            "id": str(id_),
            "label_name": f"Label of album {id_}",
            "name": f"Name of album {id_}",
            "release_date": self.random_date(),
            "type": db.AlbumType(self.random_choice(list(db.AlbumType))),
        }


class LabelGenerator(DataGenerator[LabelData, db.Label]):
    def generate_default(self, id_: int) -> LabelData:
        return {
            "is_indie": self.random_bool(),
            "is_lofi": self.random_bool(),
            "name": f"Name of label {id_}",
            "playlist_id": f"Playlist ID of label {id_}",
        }


class PlaylistGenerator(DataGenerator[PlaylistData, db.Playlist]):
    def generate_default(self, id_: int) -> PlaylistData:
        return {
            "id": str(id_),
            "image_url": None if self.random_bool() else f"Image URL for label {id_}",
            "is_editorial": self.random_bool(),
        }


class TrackGenerator(DataGenerator[TrackData, db.Track]):
    def generate_default(self, id_: int) -> TrackData:
        return {
            "album_id": f"Album ID of track {id_}",
            "id": str(id_),
            "isrc": f"ISRC of track {id_}",
            "name": f"Name of track {id_}",
            "position": id_ % 10,
        }


class TrackPopularityGenerator(DataGenerator[TrackPopularityData, db.TrackPopularity]):
    def generate_default(self, id_: int) -> TrackPopularityData:
        return {
            "date": self.random_date(),
            "popularity": int(self.random_float() * 100),
            "track_id": str(id_),
        }
