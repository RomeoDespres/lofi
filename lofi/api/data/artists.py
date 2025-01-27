from sqlalchemy import func, select

from lofi import db
from lofi.api import models


def get_artist_index(session: db.Session) -> models.ArtistIndex:
    return models.ArtistIndex.model_validate(
        {"artists": session.execute(select(db.Artist).order_by(func.lower(db.Artist.name))).scalars().all()}
    )
