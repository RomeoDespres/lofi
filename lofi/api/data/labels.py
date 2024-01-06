import datetime
from typing import Any

import pandas as pd
from sqlalchemy import Select, func, join, select

from ... import db
from .. import models


def add_quarter_popularities(df: pd.DataFrame) -> pd.DataFrame:
    """Add stream values for popularities with decimal part.

    Only quarters are added (.25, .5, .75) since this will be used to
    match quartiles.
    """
    shifted = df.shift(-1)
    dfs = {decimal: df.copy() for decimal in (0.25, 0.5, 0.75)}
    for decimal, new_df in dfs.items():
        new_df["popularity"] = df["popularity"] + decimal
        for col in "streams_q1", "streams_q3":
            # Interpolate as harmonic mean of previous and next value,
            # since popularity is a logarithmic metric
            new_df[col] = df[col] ** (1 - decimal) * shifted[col] ** decimal

    df = pd.concat([df, *(df.iloc[:-1] for df in dfs.values())])
    return df.sort_values("popularity")


def get_label_playlist_sql() -> Select[tuple[str, str]]:
    return select(db.Label.name, db.Label.playlist_id).order_by(db.Label.name)


def get_popularity_to_streams_sql() -> Select[tuple[int, int, int]]:
    max_date = select(func.max(db.PopularityStreams.date)).scalar_subquery()
    sql = (
        select(
            db.PopularityStreams.popularity,
            db.PopularityStreams.streams_q1,
            db.PopularityStreams.streams_q3,
        )
        .where(db.PopularityStreams.date == max_date)
        .order_by(db.PopularityStreams.popularity)
    )
    return sql


def get_track_popularity_sql() -> Select[tuple[str, int]]:
    six_months_ago = datetime.date.today() - datetime.timedelta(days=6 * 28)
    track_subq = (
        select(
            db.Track.isrc,
            db.Track.id,
            db.Album.release_date,
            db.Album.label_name.label("label"),
            func.row_number()
            .over(partition_by=db.Track.isrc, order_by=db.Album.release_date)
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
            .over(
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
    sql = select(track.c.label, popularity.c.popularity).select_from(
        join(track, popularity, track.c.isrc == popularity.c.isrc)
    )
    return sql


def get_labels(session: db.Session) -> models.Labels:
    tracks = sql_to_df(session, get_track_popularity_sql())

    playlists = sql_to_df(session, get_label_playlist_sql())
    playlists = playlists.set_index("name")

    streams = sql_to_df(session, get_popularity_to_streams_sql())
    streams = add_quarter_popularities(streams)
    streams = streams.set_index("popularity")

    df = (
        tracks.groupby("label")["popularity"]
        .describe()
        .sort_values("50%", ascending=False)
        .reset_index()
        .join(playlists, on="label")
        .join(streams[["streams_q1"]], on="25%")
        .join(streams[["streams_q3"]], on="75%")
    )

    labels = [
        models.Label(
            name=row["label"],
            popularity=row["50%"],
            playlist_id=row["playlist_id"],
            tracks=row["count"],
            streams=models.StreamsRange(
                min=int(row["streams_q1"]), max=int(row["streams_q3"])
            ),
        )
        for _, row in df.iterrows()
    ]

    return models.Labels(labels=labels)


def sql_to_df(session: db.Session, sql: Select[Any]) -> pd.DataFrame:
    return pd.read_sql(sql, session.connection())
