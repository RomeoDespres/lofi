import datetime
import sys
from collections.abc import Sequence

import matplotlib.pyplot as plt
import pandas as pd
from scipy.interpolate import PchipInterpolator, make_smoothing_spline
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from lofi import db


def make_smooth(x: Sequence[float], y: Sequence[float]) -> Sequence[float]:
    return make_smoothing_spline(x, y, lam=50)(x)


with db.connect() as session:
    popularity_to_streams = (
        session.execute(
            select(db.PopularityStreams).where(
                db.PopularityStreams.date.in_(select(func.max(db.PopularityStreams.date)))
            )
        )
        .scalars()
        .all()
    )

    popularity_to_streams_interpolation = PchipInterpolator(
        [p.popularity for p in popularity_to_streams], [p.streams_q2 for p in popularity_to_streams]
    )

    label = session.get(
        db.Label,
        sys.argv[1],
        options=[selectinload(db.Label.albums).selectinload(db.Album.tracks).selectinload(db.Track.popularity)],
    )
    assert label is not None
    df = pd.DataFrame(
        [
            {
                "label": label.name,
                "isrc": track.isrc,
                "release_date": album.release_date,
                "date": popularity.date,
                "popularity": popularity.popularity,
            }
            for album in label.albums
            if album.release_date
            >= (datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=365 * 2)).date()
            for track in album.tracks
            for popularity in track.popularity
        ]
    )
    df = df.groupby(["isrc", "date"]).agg({"release_date": "min", "popularity": "max"}).reset_index()
    df["age"] = (pd.to_datetime(df["date"]) - pd.to_datetime(df["release_date"])).dt.days
    df = df[
        (df["popularity"] > df.join(df.groupby("age")["popularity"].quantile(0.05).rename("q"), on="age")["q"])
        & (df["popularity"] < df.join(df.groupby("age")["popularity"].quantile(0.95).rename("q"), on="age")["q"])
    ]
    mean = df.groupby("age")["popularity"].mean().loc[0:548]
    q1 = df.groupby("age")["popularity"].apply(lambda s: s[s <= s.quantile(0.5)].mean()).loc[0:548]
    q3 = df.groupby("age")["popularity"].apply(lambda s: s[s >= s.quantile(0.5)].mean()).loc[0:548]

    smooth_mean = make_smooth(mean.index, popularity_to_streams_interpolation(mean.values) / 28)
    smooth_q1 = make_smooth(mean.index, popularity_to_streams_interpolation(q1.values) / 28)
    smooth_q3 = make_smooth(mean.index, popularity_to_streams_interpolation(q3.values) / 28)

    plt.fill_between(mean.index, smooth_q1, smooth_q3, color="#C2E0FF")
    plt.plot(mean.index, smooth_mean, color="#007FFF")
    plt.show()
