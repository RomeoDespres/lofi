from sqlalchemy import func, select
from sqlalchemy.orm import joinedload, selectinload

from lofi import db
from lofi.api import models


def get_artist_index(session: db.Session) -> models.ArtistIndex:
    return models.ArtistIndex.model_validate(
        {"artists": session.execute(select(db.Artist).order_by(func.lower(db.Artist.name))).scalars().all()}
    )


def get_artists(session: db.Session) -> list[models.Artist]:
    sql = select(db.Artist).options(
        selectinload(db.Artist.tracks).options(
            joinedload(db.Track.album).selectinload(db.Album.label).joinedload(db.Label.playlist),
            selectinload(db.Track.artists),
        ),
    )
    return [models.Artist.model_validate(artist) for artist in session.execute(sql).scalars().all()]
