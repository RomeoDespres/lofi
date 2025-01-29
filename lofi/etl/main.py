from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Literal, Protocol

from spotipy import SpotifyException  # type: ignore[import-untyped]
from sqlalchemy import func, join, select, union, update
from tqdm import tqdm

from lofi import db, env
from lofi.spotify_api import Album, Artist, ImageUrl, Playlist, SearchAlbum, SpotifyAPIClient, Track

from .errors import LabelAlreadyExistsError
from .log import LOGGER

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence


class HasIdAndName(Protocol):
    id: str
    name: str


class HasArtists(Protocol):
    @property
    def artists(self) -> Iterable[HasIdAndName]:  # pragma: no cover
        ...


def add_label(session: db.Session, label_name: str) -> None:
    LOGGER.info(f"Adding label {label_name} to database")
    if session.get(db.Label, label_name) is not None:
        raise LabelAlreadyExistsError(label_name)
    playlist = SpotifyAPIClient(session).create_playlist(
        label_name,
        f"All {label_name} releases",
        skip_if_already_exists=True,
    )
    db_playlist = session.merge(db.Playlist(id=playlist.id, is_editorial=False))
    session.add(db.Label(name=label_name, is_indie=False, playlist=db_playlist))
    session.flush()


def collect_artist_images(api: SpotifyAPIClient, session: db.Session) -> None:
    def get_image_width(image: ImageUrl) -> int:
        return 0 if image.width is None else image.width

    def get_image_url(artist: Artist, size: Literal["smallest", "largest"]) -> str | None:
        if not artist.images:
            return None

        func = min if size == "smallest" else max

        return func(artist.images, key=get_image_width).url

    ids = session.execute(select(db.Artist.id).where(db.Artist.image_url_l.is_(None))).scalars().all()
    LOGGER.info(f"Collecting {len(ids):,} artist images")
    artists = api.artists(ids)
    for artist in artists:
        session.merge(
            db.Artist(
                id=artist.id,
                name=artist.name,
                image_url_s=get_image_url(artist, "smallest"),
                image_url_l=get_image_url(artist, "largest"),
            )
        )


def collect_albums(
    api: SpotifyAPIClient,
    search_results: Sequence[SearchAlbum],
    excluded_ids: set[str] | None = None,
) -> list[Album]:
    if excluded_ids is None:
        excluded_ids = set()
    ids = list({a.id for a in search_results} - excluded_ids)
    LOGGER.info(f"Collecting {len(ids):,} albums")
    return api.albums(ids, with_all_tracks=True)


def collect_albums_popularity(api: SpotifyAPIClient, session: db.Session) -> None:
    ids = get_album_ids_with_outdated_popularity(session, max_albums=10_000)
    LOGGER.info(f"Collecting popularity for {len(ids):,} albums")
    albums = api.albums(ids)
    upload_albums_popularity(session, albums)


def collect_indie_albums(session: db.Session, labels: Sequence[db.Label], excluded_album_ids: set[str]) -> None:
    LOGGER.info("Collecting indie albums")
    api = SpotifyAPIClient(session)
    artist_ids = get_label_artist_ids(session, labels)
    LOGGER.info("Collecting indie album IDs")
    album_ids = {
        album.id
        for artist_id in tqdm(artist_ids)
        for album in api.artist_albums(artist_id)
        if album.id not in excluded_album_ids
    }
    LOGGER.info(f"Collected {len(album_ids):,} album IDs")


def collect_label_albums(session: db.Session, label: db.Label, excluded_album_ids: set[str] | None = None) -> None:
    LOGGER.info(f"Collecting label albums for {label.name}")
    if excluded_album_ids is None:
        excluded_album_ids = set()

    api = SpotifyAPIClient(session)
    search_results = search_missing_albums(api, label)
    albums = collect_albums(api, search_results, excluded_album_ids)
    albums = list(filter(lambda a: a.label == label.name, albums))
    tracks = collect_tracks(api, albums)
    upload_objects_artists(session, tracks)
    upload_objects_artists(session, albums)
    upload_albums(session, albums)
    upload_tracks(session, tracks, is_lofi=len(label.filtering_playlists) == 0)


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
    ids = get_track_ids_with_outdated_popularity(session, max_tracks=25_000)
    LOGGER.info(f"Collecting popularity for {len(ids):,} tracks")
    tracks = api.tracks(ids)
    upload_tracks_popularity(session, tracks)


def get_album_ids_with_outdated_popularity(session: db.Session, max_albums: int) -> Sequence[str]:
    sql = (
        select(db.AlbumPopularity.album_id)
        .group_by(db.AlbumPopularity.album_id)
        .order_by(func.max(db.AlbumPopularity.date).nulls_first())
        .limit(max_albums)
    )
    return session.execute(sql).scalars().all()


def get_all_album_ids(session: db.Session) -> set[str]:
    return set(session.execute(select(db.Album.id)).scalars())


def get_expected_tracklist(session: db.Session, label_name: str) -> Sequence[str]:
    subq = (
        select(
            db.Track.id,
            func.row_number().over(partition_by=db.Track.isrc, order_by=db.Album.release_date).label("track_rank"),
        )
        .select_from(join(db.Track, db.Album))
        .where(db.Album.label_name == label_name, db.Track.is_lofi)
        .order_by(db.Album.release_date.desc(), db.Album.id, db.Track.position)
        .subquery()
    )
    sql = select(subq.c.id).where(subq.c.track_rank == 1)
    return session.execute(sql).scalars().all()


def get_label_artist_ids(session: db.Session, labels: Sequence[db.Label]) -> list[str]:
    label_names = [label.name for label in labels]
    album_id_scalar_subquery = select(
        select(db.Album.id).where(db.Album.label_name.in_(label_names)).cte().c.id,
    ).scalar_subquery()
    sql = union(
        select(db.RelArtistAlbum.artist_id).where(
            db.RelArtistAlbum.album_id.in_(album_id_scalar_subquery),
        ),
        select(db.RelArtistTrack.artist_id).where(
            db.RelArtistTrack.track_id.in_(
                select(db.Track.id).where(db.Track.album_id.in_(album_id_scalar_subquery)).scalar_subquery(),
            ),
        ),
    )
    return list(session.execute(sql).scalars())


def get_label_max_albums_release_date(label: db.Label) -> datetime.date:
    if not label.albums:
        return datetime.date(2015, 1, 1)
    return max(album.release_date for album in label.albums)


def get_labels(session: db.Session) -> Sequence[db.Label]:
    sql = select(db.Label).order_by(db.Label.name).where(~db.Label.is_indie)
    return session.execute(sql).scalars().all()


def get_new_lofi_tracklist(session: db.Session) -> list[str]:
    one_week_ago = datetime.date.today() - datetime.timedelta(days=7)
    track_subq = (
        select(
            db.Track.isrc,
            db.Track.id,
            db.Album.release_date,
            func.row_number().over(partition_by=db.Track.isrc, order_by=db.Album.release_date).label("id_rank"),
        )
        .select_from(join(db.Track, db.Album).join(db.Label))
        .where(db.Label.is_lofi)
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
            .over(
                partition_by=db.TrackPopularity.track_id,
                order_by=db.TrackPopularity.date.desc(),
            )
            .label("date_rank"),
        )
        .where(
            db.TrackPopularity.track_id.in_(
                select(db.Track.id).where(db.Track.isrc.in_(select(track.c.isrc).scalar_subquery())).scalar_subquery(),
            ),
        )
        .subquery()
    )
    popularity = (
        select(
            db.Track.isrc,
            func.max(popularity_subq.c.popularity).label("popularity"),
        )
        .select_from(
            join(db.Track, popularity_subq, db.Track.id == popularity_subq.c.track_id),
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
    sql = select(db.Snapshot.track_id).where(db.Snapshot.id == snapshot_id).order_by(db.Snapshot.position)
    return list(session.execute(sql).scalars())


def get_track_ids_with_outdated_popularity(session: db.Session, max_tracks: int) -> Sequence[str]:
    sql = (
        select(db.TrackPopularity.track_id)
        .group_by(db.TrackPopularity.track_id)
        .order_by(func.max(db.TrackPopularity.date).nulls_first())
        .limit(max_tracks)
    )
    return session.execute(sql).scalars().all()


def get_tracked_playlists(session: db.Session) -> Sequence[db.Playlist]:
    sql = select(db.Playlist).where(db.Playlist.filter_for_label_name.is_not(None))
    return session.execute(sql).scalars().all()


def get_user_playlists(session: db.Session) -> dict[str, Playlist]:
    """Return an ID -> playlist mapping of all user's playlists."""
    api = SpotifyAPIClient(session)
    playlists = api.user_playlists(api.user_id)
    return {playlist.id: playlist for playlist in playlists}


def search_missing_albums(api: SpotifyAPIClient, label: db.Label) -> list[SearchAlbum]:
    LOGGER.info("Searching missing albums")
    min_year = get_label_max_albums_release_date(label)
    search_results: list[SearchAlbum] = []
    for year in range(min_year.year, datetime.date.today().year + 1):
        criteria = [f"year:{year}", *[f"label:{word}" for word in label.name.split()]]
        search_results.extend(api.search_albums(" ".join(criteria)))
    return search_results


@db.with_connection
def run(session: db.Session) -> None:
    playlists = get_user_playlists(session)
    for i, label in enumerate(labels := get_labels(session)):
        LOGGER.info(f"{i + 1}/{len(labels)} Collecting data for {label.name}")
        collect_label_albums(session, label, excluded_album_ids=get_all_album_ids(session))
        update_playlist(session, label, playlists[label.playlist_id])
    collect_popularity(session)
    collect_artist_images(SpotifyAPIClient(session), session)
    update_new_lofi(session)
    update_playlist_images(session, playlists.values())
    update_tracked_playlists(session)
    update_track_is_lofi(session)


def snapshot_is_in_db(session: db.Session, snapshot_id: str) -> bool:
    sql = select(db.Snapshot.id).where(db.Snapshot.id == snapshot_id).limit(1)
    return session.execute(sql).scalar_one_or_none() is not None


def update_playlist(session: db.Session, label: db.Label, playlist: Playlist) -> None:
    api = SpotifyAPIClient(session)
    expected_tracklist = get_expected_tracklist(session, label.name)
    snapshot = get_snapshot(session, playlist.snapshot_id)
    api.set_playlist_tracks(label.playlist_id, expected_tracklist, snapshot or None)
    new_snapshot_id = api.playlist(label.playlist_id).snapshot_id
    upload_snapshot(session, playlist.id, new_snapshot_id, expected_tracklist)


def update_playlist_images(session: db.Session, playlists: Iterable[Playlist]) -> None:
    def get_image_width(image: ImageUrl) -> int:
        return 0 if image.width is None else image.width

    def get_image_url(playlist: Playlist) -> str | None:
        if not playlist.images:
            return None
        return min(playlist.images, key=get_image_width).url

    for playlist in playlists:
        db_playlist = session.get(db.Playlist, playlist.id)
        if db_playlist is None:
            continue
        db_playlist.image_url = get_image_url(playlist)

    session.flush()


def update_new_lofi(session: db.Session) -> None:
    LOGGER.info("Updating new lofi")
    api = SpotifyAPIClient(session)
    tracklist = get_new_lofi_tracklist(session)
    api.set_playlist_tracks(env.new_lofi_playlist_id(), tracklist, use_reorders=True)


def update_track_is_lofi(session: db.Session) -> None:
    LOGGER.info("Updating track.is_lofi with filtering playlists")
    filtering_playlist_ids = select(db.Playlist.id).where(db.Playlist.filter_for_label_name.is_not(None))
    filtering_playlist_track_ids = (
        select(db.Snapshot.track_id).where(db.Snapshot.playlist_id.in_(filtering_playlist_ids)).distinct()
    )
    sql = update(db.Track).where(~db.Track.is_lofi, db.Track.id.in_(filtering_playlist_track_ids)).values(is_lofi=True)
    session.execute(sql)


def update_tracked_playlists(session: db.Session) -> None:
    LOGGER.info("Updating tracked playlists")
    api = SpotifyAPIClient(session)
    not_found_http_status = 404
    for playlist in tqdm(get_tracked_playlists(session)):
        try:
            spotify_playlist = api.playlist(playlist.id)
        except SpotifyException as e:
            if e.http_status == not_found_http_status:
                # This playlist does not exist anymore!
                continue
            raise
        if snapshot_is_in_db(session, spotify_playlist.snapshot_id):
            continue
        track_ids = [t.id for t in api.playlist_tracks(playlist.id)]
        upload_snapshot(session, playlist.id, spotify_playlist.snapshot_id, track_ids)


def upload_album_popularity(session: db.Session, album: Album) -> None:
    popularity = db.AlbumPopularity(
        album_id=album.id,
        date=datetime.date.today(),
        popularity=album.popularity,
    )
    session.merge(popularity)


def upload_albums(session: db.Session, albums: Sequence[Album]) -> None:
    LOGGER.info(f"Uploading {len(albums):,} albums")

    def get_image_width(image: ImageUrl) -> int:
        return 0 if image.width is None else image.width

    def get_image_url(album: Album, size: Literal["smallest", "largest"]) -> str | None:
        if not album.images:
            return None

        func = min if size == "smallest" else max

        return func(album.images, key=get_image_width).url

    for album in tqdm(albums):
        if session.get(db.Label, album.label) is None:
            session.merge(
                db.Label(
                    name=album.label,
                    is_lofi=True,
                    is_indie=True,
                    playlist=session.merge(db.Playlist(id="")),
                ),
            )
        session.merge(
            db.Album(
                id=album.id,
                image_url_l=get_image_url(album, "largest"),
                image_url_s=get_image_url(album, "smallest"),
                label_name=album.label,
                name=album.name,
                release_date=album.release_date,
                type=album.album_type,
            ),
        )
        upload_album_popularity(session, album)
        for artist_position, artist in enumerate(album.artists):
            session.merge(
                db.RelArtistAlbum(
                    artist_id=artist.id,
                    album_id=album.id,
                    artist_position=artist_position,
                ),
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
    session: db.Session,
    playlist_id: str,
    snapshot_id: str,
    track_ids: Iterable[str],
) -> None:
    LOGGER.info("Uploading playlist snapshot")
    if snapshot_is_in_db(session, snapshot_id):
        LOGGER.info("Snapshot already in database, skipping")
        return
    timestamp = datetime.datetime.now(datetime.UTC)
    for position, track_id in enumerate(tqdm(track_ids)):
        snapshot = db.Snapshot(
            id=snapshot_id,
            position=position,
            playlist_id=playlist_id,
            timestamp=timestamp,
            track_id=track_id,
        )
        session.merge(snapshot)


def upload_track_popularity(session: db.Session, track: Track) -> None:
    popularity = db.TrackPopularity(track_id=track.id, date=datetime.date.today(), popularity=track.popularity)
    session.merge(popularity)


def upload_tracks(session: db.Session, tracks: Sequence[Track], *, is_lofi: bool) -> None:
    LOGGER.info(f"Uploading {len(tracks):,} tracks")
    for track in tqdm(tracks):
        session.merge(
            db.Track(
                album_id=track.album.id,
                id=track.id,
                is_lofi=is_lofi,
                isrc=track.external_ids.isrc,
                name=track.name,
                position=track.track_number,
            ),
        )
        upload_track_popularity(session, track)
        for artist_position, artist in enumerate(track.artists):
            session.merge(
                db.RelArtistTrack(
                    artist_id=artist.id,
                    track_id=track.id,
                    artist_position=artist_position,
                ),
            )


def upload_tracks_popularity(session: db.Session, tracks: Sequence[Track]) -> None:
    LOGGER.info(f"Uploading popularity for {len(tracks):,} tracks")
    for track in tracks:
        upload_track_popularity(session, track)
