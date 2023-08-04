from __future__ import annotations

import datetime
from typing import TypeVar
from enum import StrEnum

from humps import decamelize
from sqlalchemy import ForeignKey, MetaData
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)


_T = TypeVar("_T")


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_N_label)s",
            "uq": "uq_%(table_name)s_%(column_0_N_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return decamelize(cls.__name__)


class RelArtistAlbum(Base):
    album_id: Mapped[str] = mapped_column(
        ForeignKey("album.id"), primary_key=True, comment="Spotify album ID"
    )
    artist_id: Mapped[str] = mapped_column(
        ForeignKey("artist.id"), primary_key=True, comment="Spotify artist ID"
    )
    artist_position: Mapped[int] = mapped_column(
        primary_key=True,
        comment="Position of the artist in the list of all artists of the album",
    )


class RelArtistTrack(Base):
    track_id: Mapped[str] = mapped_column(
        ForeignKey("track.id"), primary_key=True, comment="Spotify track ID"
    )
    artist_id: Mapped[str] = mapped_column(
        ForeignKey("artist.id"), primary_key=True, comment="Spotify artist ID"
    )
    artist_position: Mapped[int] = mapped_column(
        primary_key=True,
        comment="Position of the artist in the list of all artists of the album",
    )


class Label(Base):
    name: Mapped[str] = mapped_column(
        primary_key=True, comment="Name of the record label"
    )
    playlist_id: Mapped[str] = mapped_column(
        ForeignKey("playlist.id"),
        comment="Spotify ID of the playlist containing label releases.",
    )

    albums: Mapped[list[Album]] = relationship(back_populates="label")
    playlist: Mapped[Playlist] = relationship()


class Artist(Base):
    id: Mapped[str] = mapped_column(primary_key=True, comment="Spotify artist ID")
    name: Mapped[str] = mapped_column(comment="Name of the artist")

    albums: Mapped[list[Album]] = relationship(
        back_populates="artists",
        secondary=RelArtistAlbum.__table__,
        order_by="Album.release_date",
    )


class AlbumType(StrEnum):
    album = "album"
    compilation = "compilation"
    single = "single"


class Album(Base):
    id: Mapped[str] = mapped_column(primary_key=True, comment="Spotify album ID")
    label_name: Mapped[str] = mapped_column(
        ForeignKey(Label.name), comment="Name of the record label of the album"
    )
    name: Mapped[str] = mapped_column(comment="Name of the album")
    release_date: Mapped[datetime.date] = mapped_column(
        comment="Release date of the album"
    )
    type: Mapped[AlbumType] = mapped_column(
        comment="Type of the album ('album', 'compilation', or 'single')"
    )

    artists: Mapped[list[Artist]] = relationship(
        back_populates="albums",
        secondary=RelArtistAlbum.__table__,
        order_by=RelArtistAlbum.artist_position,
    )
    label: Mapped[Label] = relationship(back_populates="albums")
    popularity: Mapped[list[AlbumPopularity]] = relationship(back_populates="album")
    tracks: Mapped[list[Track]] = relationship(
        back_populates="album", order_by="Track.position"
    )


class AlbumPopularity(Base):
    album_id: Mapped[str] = mapped_column(
        ForeignKey(Album.id), primary_key=True, comment="Spotify album ID"
    )
    date: Mapped[datetime.date] = mapped_column(
        primary_key=True, comment="Date at which popularity was collected"
    )
    popularity: Mapped[int] = mapped_column("Spotify popularity")

    album: Mapped[Album] = relationship(back_populates="popularity")


class Track(Base):
    id: Mapped[str] = mapped_column(primary_key=True, comment="Spotify track ID")
    album_id: Mapped[str] = mapped_column(
        ForeignKey(Album.id), comment="Spotify ID of the album of the track"
    )
    isrc: Mapped[str] = mapped_column(comment="ISRC of the track")
    name: Mapped[str] = mapped_column(comment="Name of the track")
    position: Mapped[int] = mapped_column(
        comment="Position of the track within its album"
    )

    album: Mapped[Album] = relationship(back_populates="tracks")
    artists: Mapped[list[Artist]] = relationship(
        secondary=RelArtistTrack.__table__, order_by=RelArtistTrack.artist_position
    )
    popularity: Mapped[list[TrackPopularity]] = relationship(back_populates="track")


class TrackPopularity(Base):
    track_id: Mapped[str] = mapped_column(
        ForeignKey(Track.id), primary_key=True, comment="Spotify track ID"
    )
    date: Mapped[datetime.date] = mapped_column(
        primary_key=True, comment="Date at which popularity was collected"
    )
    popularity: Mapped[int] = mapped_column("Spotify popularity")

    track: Mapped[Track] = relationship(back_populates="popularity")


class Playlist(Base):
    id: Mapped[str] = mapped_column(primary_key=True, comment="Spotify playlist ID")


class Snapshot(Base):
    id: Mapped[str] = mapped_column(
        primary_key=True, comment="Spotify playlist snapshot ID"
    )
    position: Mapped[int] = mapped_column(
        primary_key=True, comment="Track position within playlist"
    )
    track_id: Mapped[str] = mapped_column(comment="Spotify track ID")


class User(Base):
    id: Mapped[str] = mapped_column(primary_key=True, comment="Spotify user ID")
    token: Mapped[str | None] = mapped_column(comment="Spotipy cached token.")
