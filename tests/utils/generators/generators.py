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
    def generate_default(self, id: int) -> AlbumData:
        return {
            "id": str(id),
            "label_name": f"Label of album {id}",
            "name": f"Name of album {id}",
            "release_date": self.random_date(),
            "type": db.AlbumType(self.random_choice(list(db.AlbumType))),
        }


class LabelGenerator(DataGenerator[LabelData, db.Label]):
    def generate_default(self, id: int) -> LabelData:
        return {
            "is_indie": self.random_bool(),
            "is_lofi": self.random_bool(),
            "name": f"Name of label {id}",
            "playlist_id": f"Playlist ID of label {id}",
            "playlist_image_url": None
            if self.random_bool()
            else f"Image URL for label {id}",
        }


class PlaylistGenerator(DataGenerator[PlaylistData, db.Playlist]):
    def generate_default(self, id: int) -> PlaylistData:
        return {"id": str(id)}


class TrackGenerator(DataGenerator[TrackData, db.Track]):
    def generate_default(self, id: int) -> TrackData:
        return {
            "album_id": f"Album ID of track {id}",
            "id": str(id),
            "isrc": f"ISRC of track {id}",
            "name": f"Name of track {id}",
            "position": id % 10,
        }


class TrackPopularityGenerator(DataGenerator[TrackPopularityData, db.TrackPopularity]):
    def generate_default(self, id: int) -> TrackPopularityData:
        return {
            "date": self.random_date(),
            "popularity": int(self.random_float() * 100),
            "track_id": str(id),
        }
