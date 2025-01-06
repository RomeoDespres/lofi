from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING, Literal

import pytest

import alembic.command
import alembic.config
import lofi.db.connection
import lofi.etl.log
import lofi.log
import lofi.spotify_api.log
from lofi import db, log
from lofi.db.connection import get_temp_file_path

from .utils import AlbumGenerator, LabelGenerator, PlaylistGenerator, TrackGenerator, TrackPopularityGenerator

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture
def album_generator() -> AlbumGenerator:
    return AlbumGenerator()


@pytest.fixture
def label_generator() -> LabelGenerator:
    return LabelGenerator()


@pytest.fixture(autouse=True)
def _no_spotify_user_id(monkeypatch: pytest.MonkeyPatch) -> None:
    """Temporarily delete the `SPOTIFY_USER_ID` environement variable.

    Prevents unwanted API calls against a true Spotify profile.
    """
    monkeypatch.delenv("SPOTIFY_USER_ID", raising=False)


@pytest.fixture
def _patch_connect(temp_db_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    original_connect = lofi.db.connect
    monkeypatch.setattr(lofi.db, "connect", lambda: original_connect(str(temp_db_path.absolute())))


@pytest.fixture(autouse=True)
def _patch_loggers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(lofi.log, "LOGGER", log.get_logger("lofi:test"))
    monkeypatch.setattr(lofi.etl.log, "LOGGER", log.get_logger("lofi:test:etl"))
    monkeypatch.setattr(lofi.spotify_api.log, "LOGGER", log.get_logger("lofi:test:spotify_api"))


@pytest.fixture
def playlist_generator() -> PlaylistGenerator:
    return PlaylistGenerator()


def run_alembic_migrations(session: db.Session, migration_type: Literal["upgrade", "downgrade"] = "upgrade") -> None:
    """Upgrade temp DB to latest Alembic version."""
    config_path = pathlib.Path(__file__).parent.parent / "alembic.ini"
    config = alembic.config.Config(str(config_path))
    config.attributes["session"] = session
    if migration_type == "upgrade":
        alembic.command.upgrade(config, "head")
    elif migration_type == "downgrade":
        alembic.command.downgrade(config, "base")
    else:
        msg = f"`type` must be 'upgrade' or 'downgrade', received {migration_type!r}"
        raise ValueError(msg)


@pytest.fixture
def session(temp_db_path: pathlib.Path) -> Iterator[db.Session]:
    """Yield a SQLAlchemy session connected to a test database.

    Session is rolled back on exit.

    Yields
    ------
    Connected SQLAlchemy session.

    """
    with db.connect(str(temp_db_path.absolute())) as session:
        run_alembic_migrations(session, "upgrade")
        yield session
        session.rollback()


@pytest.fixture
def temp_db_path() -> Iterator[pathlib.Path]:
    with get_temp_file_path() as temp_path:
        yield temp_path


@pytest.fixture
def track_generator() -> TrackGenerator:
    return TrackGenerator()


@pytest.fixture
def track_popularity_generator() -> TrackPopularityGenerator:
    return TrackPopularityGenerator()
