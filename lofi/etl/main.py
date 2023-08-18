import datetime
from typing import Iterable, Protocol, Sequence

from sqlalchemy import func, join, select
from tqdm import tqdm

from .. import db
from .. import env
from ..spotify_api import Album, SearchAlbum, SpotifyAPIClient, Track
from .errors import LabelAlreadyExistsError
from .log import LOGGER


class HasIdAndName(Protocol):
    id: str
    name: str


class HasArtists(Protocol):
    @property
    def artists(self) -> Iterable[HasIdAndName]:
        ...


def add_label(session: db.Session, label_name: str) -> None:
    LOGGER.info(f"Adding label {label_name} to database")
    if session.get(db.Label, label_name) is not None:
        raise LabelAlreadyExistsError(label_name)
    playlist = SpotifyAPIClient(session).create_playlist(
        label_name, f"All {label_name} releases", skip_if_already_exists=True
    )
    db_playlist = session.merge(db.Playlist(id=playlist.id))
    session.add(db.Label(name=label_name, playlist=db_playlist))
    session.flush()


def collect_albums(
    api: SpotifyAPIClient,
    search_results: Sequence[SearchAlbum],
    excluded_ids: set[str] = set(),
) -> list[Album]:
    ids = list({a.id for a in search_results} - excluded_ids)
    LOGGER.info(f"Collecting {len(ids):,} albums")
    return api.albums(ids, with_all_tracks=True)


def collect_albums_popularity(api: SpotifyAPIClient, session: db.Session) -> None:
    ids = get_album_ids_with_outdated_popularity(session)
    LOGGER.info(f"Collecting popularity for {len(ids):,} albums")
    albums = api.albums(ids)
    upload_albums_popularity(session, albums)


def collect_label_albums(
    session: db.Session, label: db.Label, excluded_album_ids: set[str] = set()
) -> None:
    LOGGER.info(f"Collecting label albums for {label.name}")
    api = SpotifyAPIClient(session)
    search_results = search_missing_albums(api, label)
    albums = collect_albums(api, search_results, excluded_album_ids)
    albums = list(filter(lambda a: a.label == label.name, albums))
    tracks = collect_tracks(api, albums)
    upload_objects_artists(session, tracks)
    upload_objects_artists(session, albums)
    upload_albums(session, albums)
    upload_tracks(session, tracks)


def collect_popularity(session: db.Session) -> None:
    LOGGER.info("Collecting popularity")
    api = SpotifyAPIClient(session)
    collect_albums_popularity(api, session)
    collect_tracks_popularity(api, session)


def collect_tracks(api: SpotifyAPIClient, albums: Sequence[Album]) -> list[Track]:
    LOGGER.info(f"Collecting tracks for {len(albums):,} albums")
    ids = list({t.id for album in albums for t in album.tracks.items})
    return api.tracks(ids)


def collect_tracks_popularity(api: SpotifyAPIClient, session: db.Session) -> None:
    ids = get_track_ids_with_outdated_popularity(session)
    LOGGER.info(f"Collecting popularity for {len(ids):,} tracks")
    tracks = api.tracks(ids)
    upload_tracks_popularity(session, tracks)


def get_album_ids_with_outdated_popularity(session: db.Session) -> Sequence[str]:
    sql = select(db.Album.id).where(
        db.Album.id.not_in(
            select(db.AlbumPopularity.album_id)
            .where(db.AlbumPopularity.date == datetime.date.today())
            .scalar_subquery()
        )
    )
    return session.execute(sql).scalars().all()


def get_all_album_ids(session: db.Session) -> set[str]:
    return set(session.execute(select(db.Album.id)).scalars())


def get_expected_tracklist(session: db.Session, label_name: str) -> Sequence[str]:
    subq = (
        select(
            db.Track.id,
            func.row_number()
            .over(  # type: ignore[no-untyped-call]
                partition_by=db.Track.isrc, order_by=db.Album.release_date
            )
            .label("track_rank"),
        )
        .select_from(join(db.Track, db.Album))
        .where(db.Album.label_name == label_name)
        .order_by(db.Album.release_date.desc(), db.Album.id, db.Track.position)
        .subquery()
    )
    sql = select(subq.c.id).where(subq.c.track_rank == 1)
    return session.execute(sql).scalars().all()


def get_label_max_albums_release_date(label: db.Label) -> datetime.date:
    if not label.albums:
        return datetime.date(2015, 1, 1)
    return max(album.release_date for album in label.albums)


def get_labels(session: db.Session) -> Sequence[db.Label]:
    return session.execute(select(db.Label).order_by(db.Label.name)).scalars().all()


def get_new_lofi_tracklist(session: db.Session) -> list[str]:
    one_week_ago = datetime.date.today() - datetime.timedelta(days=7)
    track_subq = (
        select(
            db.Track.isrc,
            db.Track.id,
            db.Album.release_date,
            func.row_number()
            .over(  # type: ignore[no-untyped-call]
                partition_by=db.Track.isrc, order_by=db.Album.release_date
            )
            .label("id_rank"),
        )
        .select_from(join(db.Track, db.Album))
        .subquery()
    )
    track = (
        select(track_subq.c.isrc, track_subq.c.id)
        .where(track_subq.c.id_rank == 1, track_subq.c.release_date > one_week_ago)
        .cte()
    )
    popularity_subq = (
        select(
            db.TrackPopularity.track_id,
            db.TrackPopularity.popularity,
            func.row_number()
            .over(  # type: ignore[no-untyped-call]
                partition_by=db.TrackPopularity.track_id,
                order_by=db.TrackPopularity.date.desc(),
            )
            .label("date_rank"),
        )
        .where(
            db.TrackPopularity.track_id.in_(
                select(db.Track.id)
                .where(db.Track.isrc.in_(select(track.c.isrc).scalar_subquery()))
                .scalar_subquery()
            )
        )
        .subquery()
    )
    popularity = (
        select(
            db.Track.isrc, func.max(popularity_subq.c.popularity).label("popularity")
        )
        .select_from(
            join(db.Track, popularity_subq, db.Track.id == popularity_subq.c.track_id)
        )
        .where(popularity_subq.c.date_rank == 1)
        .group_by(db.Track.isrc)
        .subquery()
    )
    sql = (
        select(track.c.id)
        .select_from(join(track, popularity, track.c.isrc == popularity.c.isrc))
        .order_by(popularity.c.popularity.desc())
    )
    return list(session.execute(sql).scalars())


def get_snapshot(session: db.Session, snapshot_id: str) -> list[str]:
    sql = (
        select(db.Snapshot.track_id)
        .where(db.Snapshot.id == snapshot_id)
        .order_by(db.Snapshot.position)
    )
    return list(session.execute(sql).scalars())


def get_track_ids_with_outdated_popularity(session: db.Session) -> Sequence[str]:
    sql = select(db.Track.id).where(
        db.Track.id.not_in(
            select(db.TrackPopularity.track_id)
            .where(db.TrackPopularity.date == datetime.date.today())
            .scalar_subquery()
        )
    )
    return session.execute(sql).scalars().all()


def search_missing_albums(api: SpotifyAPIClient, label: db.Label) -> list[SearchAlbum]:
    LOGGER.info("Searching missing albums")
    min_year = get_label_max_albums_release_date(label)
    search_results: list[SearchAlbum] = []
    for year in range(min_year.year, datetime.date.today().year + 1):
        search_results.extend(api.search_albums(f'label:"{label.name}" year:{year}'))
    return search_results


@db.with_connection
def run(session: db.Session) -> None:
    for i, label in enumerate(labels := get_labels(session)):
        LOGGER.info(f"{i + 1}/{len(labels)} Collecting data for {label.name}")
        collect_label_albums(
            session, label, excluded_album_ids=get_all_album_ids(session)
        )
        update_playlist(session, label)
    collect_popularity(session)
    update_new_lofi(session)


def update_playlist(session: db.Session, label: db.Label) -> None:
    api = SpotifyAPIClient(session)
    expected_tracklist = get_expected_tracklist(session, label.name)
    snapshot = get_snapshot(session, api.snapshot_id(label.playlist_id))
    api.set_playlist_tracks(label.playlist_id, expected_tracklist, snapshot or None)
    upload_snapshot(session, api.snapshot_id(label.playlist_id), expected_tracklist)


def update_new_lofi(session: db.Session) -> None:
    LOGGER.info("Updating new lofi")
    api = SpotifyAPIClient(session)
    tracklist = get_new_lofi_tracklist(session)
    api.set_playlist_tracks(env.new_lofi_playlist_id(), tracklist)


def upload_album_popularity(session: db.Session, album: Album) -> None:
    popularity = db.AlbumPopularity(
        album_id=album.id, date=datetime.date.today(), popularity=album.popularity
    )
    session.merge(popularity)


def upload_albums(session: db.Session, albums: Sequence[Album]) -> None:
    LOGGER.info(f"Uploading {len(albums):,} albums")
    for album in tqdm(albums):
        session.merge(
            db.Album(
                id=album.id,
                label_name=album.label,
                name=album.name,
                release_date=album.release_date,
                type=album.album_type,
            )
        )
        upload_album_popularity(session, album)
        for artist_position, artist in enumerate(album.artists):
            session.merge(
                db.RelArtistAlbum(
                    artist_id=artist.id,
                    album_id=album.id,
                    artist_position=artist_position,
                )
            )


def upload_albums_popularity(session: db.Session, albums: Sequence[Album]) -> None:
    LOGGER.info(f"Uploading popularity for {len(albums):,} albums")
    for album in tqdm(albums):
        upload_album_popularity(session, album)


def upload_objects_artists(session: db.Session, objs: Iterable[HasArtists]) -> None:
    LOGGER.info("Uploading artists")
    unique_artists = {artist.id: artist for obj in objs for artist in obj.artists}
    for artist in tqdm(unique_artists.values()):
        session.merge(db.Artist(id=artist.id, name=artist.name))


def upload_snapshot(
    session: db.Session, snapshot_id: str, track_ids: Iterable[str]
) -> None:
    LOGGER.info("Uploading playlist snapshot")
    sql = select(db.Snapshot.id).where(db.Snapshot.id == snapshot_id).limit(1)
    if session.execute(sql).scalar_one_or_none() is not None:
        LOGGER.info("Snapshot already in database, skipping")
        return
    for position, track_id in enumerate(tqdm(track_ids)):
        session.merge(db.Snapshot(id=snapshot_id, position=position, track_id=track_id))


def upload_track_popularity(session: db.Session, track: Track) -> None:
    popularity = db.TrackPopularity(
        track_id=track.id, date=datetime.date.today(), popularity=track.popularity
    )
    session.merge(popularity)


def upload_tracks(session: db.Session, tracks: Sequence[Track]) -> None:
    LOGGER.info(f"Uploading {len(tracks):,} tracks")
    for track in tqdm(tracks):
        session.merge(
            db.Track(
                album_id=track.album.id,
                id=track.id,
                isrc=track.external_ids.isrc,
                name=track.name,
                position=track.track_number,
            )
        )
        upload_track_popularity(session, track)
        for artist_position, artist in enumerate(track.artists):
            session.merge(
                db.RelArtistTrack(
                    artist_id=artist.id,
                    track_id=track.id,
                    artist_position=artist_position,
                )
            )


def upload_tracks_popularity(session: db.Session, tracks: Sequence[Track]) -> None:
    LOGGER.info(f"Uploading popularity for {len(tracks):,} tracks")
    for track in tracks:
        upload_track_popularity(session, track)
