import datetime

import pandas as pd
from sqlalchemy import func, join, select

from lofi import db


six_months_ago = datetime.date.today() - datetime.timedelta(days=6 * 28)
track_subq = (
    select(
        db.Track.isrc,
        db.Track.id,
        db.Album.release_date,
        db.Album.label_name.label("label"),
        func.row_number()
        .over(  # type: ignore[no-untyped-call]
            partition_by=db.Track.isrc, order_by=db.Album.release_date
        )
        .label("id_rank"),
    )
    .select_from(join(db.Track, db.Album))
    .where(db.Album.label_name != "Inside Records")
    .subquery()
)
track = (
    select(track_subq.c.id, track_subq.c.isrc, track_subq.c.label)
    .where(track_subq.c.id_rank == 1, track_subq.c.release_date > six_months_ago)
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
    select(db.Track.isrc, func.max(popularity_subq.c.popularity).label("popularity"))
    .select_from(
        join(db.Track, popularity_subq, db.Track.id == popularity_subq.c.track_id)
    )
    .where(popularity_subq.c.date_rank == 1)
    .group_by(db.Track.isrc)
    .subquery()
)
sql = select(track.c.label, popularity.c.popularity).select_from(
    join(track, popularity, track.c.isrc == popularity.c.isrc)
)


with db.connect() as session:
    df = pd.read_sql(sql, session.connection())
    playlists = pd.read_sql(
        select(db.Label.name, db.Label.playlist_id).order_by(db.Label.name),
        session.connection(),
    )

stats = (
    df.groupby("label")["popularity"]
    .describe()
    .sort_values("50%", ascending=False)
    .reset_index()
)
stats.to_clipboard(index=False, sep="\t", header=False, decimal=",")
input("Copied stats data! Paste into FULL LEADERBOARD and hit Enter")
playlists.to_clipboard(index=False, header=False, sep="\t")
input("Copied playlists data! Paste into PLAYLISTS and hit Enter")
