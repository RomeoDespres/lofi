from __future__ import annotations

import datetime  # noqa: TC003
from enum import StrEnum

from humps import decamelize
from sqlalchemy import BigInteger, ForeignKey, MetaData, literal
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column, relationship


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_N_label)s",
            "uq": "uq_%(table_name)s_%(column_0_N_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        },
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        return decamelize(cls.__name__)


class RelArtistAlbum(Base):
    album_id: Mapped[str] = mapped_column(
        ForeignKey("album.id"),
        primary_key=True,
        comment="Spotify album ID",
    )
    artist_id: Mapped[str] = mapped_column(
        ForeignKey("artist.id"),
        primary_key=True,
        comment="Spotify artist ID",
    )
    artist_position: Mapped[int] = mapped_column(
        primary_key=True,
        comment="Position of the artist in the list of all artists of the album",
    )


class RelArtistTrack(Base):
    track_id: Mapped[str] = mapped_column(
        ForeignKey("track.id"),
        primary_key=True,
        comment="Spotify track ID",
    )
    artist_id: Mapped[str] = mapped_column(
        ForeignKey("artist.id"),
        primary_key=True,
        comment="Spotify artist ID",
    )
    artist_position: Mapped[int] = mapped_column(
        primary_key=True,
        comment="Position of the artist in the list of all artists of the album",
    )


class Label(Base):
    name: Mapped[str] = mapped_column(
        primary_key=True,
        comment="Name of the record label",
    )
    is_indie: Mapped[bool] = mapped_column(
        comment="Whether this label is independent from tracked labels.",
    )
    is_lofi: Mapped[bool] = mapped_column(
        comment="Whether this label is a lofi label. "
        "If False, will not be included in stats reports and new lofi playlist.",
        server_default=literal(value=True),
    )
    playlist_id: Mapped[str] = mapped_column(
        ForeignKey("playlist.id"),
        comment="Spotify ID of the playlist containing label releases.",
    )

    albums: Mapped[list[Album]] = relationship(back_populates="label")
    filtering_playlists: Mapped[list[Playlist]] = relationship(
        back_populates="filter_for_label", foreign_keys="Playlist.filter_for_label_name"
    )
    playlist: Mapped[Playlist] = relationship(foreign_keys=[playlist_id])


class Artist(Base):
    id: Mapped[str] = mapped_column(primary_key=True, comment="Spotify artist ID")
    image_url_s: Mapped[str | None] = mapped_column(comment="Spotify artist profile picture URL (small size)")
    image_url_l: Mapped[str | None] = mapped_column(comment="Spotify artist profile picture URL (large size)")
    name: Mapped[str] = mapped_column(comment="Name of the artist")

    albums: Mapped[list[Album]] = relationship(
        back_populates="artists", secondary=RelArtistAlbum.__table__, order_by="Album.release_date"
    )
    tracks: Mapped[list[Track]] = relationship(back_populates="artists", secondary=RelArtistTrack.__table__)


class AlbumType(StrEnum):
    album = "album"
    compilation = "compilation"
    single = "single"


class Album(Base):
    id: Mapped[str] = mapped_column(primary_key=True, comment="Spotify album ID")
    image_url_s: Mapped[str | None] = mapped_column(comment="Spotify album cover URL (small size)")
    image_url_l: Mapped[str | None] = mapped_column(comment="Spotify album cover URL (large size)")
    label_name: Mapped[str] = mapped_column(
        ForeignKey(Label.name),
        comment="Name of the record label of the album",
    )
    name: Mapped[str] = mapped_column(comment="Name of the album")
    release_date: Mapped[datetime.date] = mapped_column(
        comment="Release date of the album",
    )
    type: Mapped[AlbumType] = mapped_column(
        comment="Type of the album ('album', 'compilation', or 'single')",
    )

    artists: Mapped[list[Artist]] = relationship(
        back_populates="albums",
        secondary=RelArtistAlbum.__table__,
        order_by=RelArtistAlbum.artist_position,
    )
    label: Mapped[Label] = relationship(back_populates="albums")
    popularity: Mapped[list[AlbumPopularity]] = relationship(back_populates="album")
    tracks: Mapped[list[Track]] = relationship(
        back_populates="album",
        order_by="Track.position",
    )


class AlbumPopularity(Base):
    album_id: Mapped[str] = mapped_column(
        ForeignKey(Album.id),
        primary_key=True,
        comment="Spotify album ID",
    )
    date: Mapped[datetime.date] = mapped_column(
        primary_key=True,
        comment="Date at which popularity was collected",
    )
    popularity: Mapped[int] = mapped_column("Spotify popularity")

    album: Mapped[Album] = relationship(back_populates="popularity")


class Track(Base):
    id: Mapped[str] = mapped_column(primary_key=True, comment="Spotify track ID")
    album_id: Mapped[str] = mapped_column(
        ForeignKey(Album.id),
        comment="Spotify ID of the album of the track",
    )
    is_lofi: Mapped[bool] = mapped_column(server_default=literal(value=True))
    isrc: Mapped[str] = mapped_column(comment="ISRC of the track")
    name: Mapped[str] = mapped_column(comment="Name of the track")
    position: Mapped[int] = mapped_column(
        comment="Position of the track within its album",
    )

    album: Mapped[Album] = relationship(back_populates="tracks")
    artists: Mapped[list[Artist]] = relationship(
        secondary=RelArtistTrack.__table__,
        order_by=RelArtistTrack.artist_position,
    )
    popularity: Mapped[list[TrackPopularity]] = relationship(back_populates="track")


class TrackPopularity(Base):
    track_id: Mapped[str] = mapped_column(
        ForeignKey(Track.id),
        primary_key=True,
        comment="Spotify track ID",
    )
    date: Mapped[datetime.date] = mapped_column(
        primary_key=True,
        comment="Date at which popularity was collected",
    )
    popularity: Mapped[int] = mapped_column(comment="Spotify popularity")

    track: Mapped[Track] = relationship(back_populates="popularity")


class Playlist(Base):
    id: Mapped[str] = mapped_column(primary_key=True, comment="Spotify playlist ID")
    image_url: Mapped[str | None] = mapped_column(comment="Cover image URL of the playlist")
    is_editorial: Mapped[bool] = mapped_column(comment="Whether playlist is a Spotify editorial playlist")
    filter_for_label_name: Mapped[str | None] = mapped_column(ForeignKey(Label.name))

    filter_for_label: Mapped[Label] = relationship(
        back_populates="filtering_playlists", foreign_keys=[filter_for_label_name]
    )
    snapshots: Mapped[list[Snapshot]] = relationship(back_populates="playlist")


class PopularityStreams(Base):
    date: Mapped[datetime.date] = mapped_column(primary_key=True)
    popularity: Mapped[int] = mapped_column(primary_key=True)
    streams_q1: Mapped[int] = mapped_column(BigInteger)
    streams_q2: Mapped[int] = mapped_column(BigInteger)
    streams_q3: Mapped[int] = mapped_column(BigInteger)


class Snapshot(Base):
    id: Mapped[str] = mapped_column(
        primary_key=True,
        comment="Spotify playlist snapshot ID",
    )
    position: Mapped[int] = mapped_column(
        primary_key=True,
        comment="Track position within playlist",
    )
    playlist_id: Mapped[str | None] = mapped_column(
        ForeignKey(Playlist.id),
        comment="Id of this snapshot's playlist. NULL for historical values where it wasn't recorded",
        index=True,
    )
    timestamp: Mapped[datetime.datetime | None] = mapped_column(
        comment="Timestamp at which snapshot was captured. NULL for historical values where it wasn't recorded",
    )
    track_id: Mapped[str] = mapped_column(comment="Spotify track ID", index=True)

    playlist: Mapped[Playlist | None] = relationship(back_populates="snapshots")


class User(Base):
    id: Mapped[str] = mapped_column(primary_key=True, comment="Spotify user ID")
    token: Mapped[str | None] = mapped_column(comment="Spotipy cached token.")
