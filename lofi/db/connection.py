from __future__ import annotations

import contextlib
import functools
import gzip
import os
import pathlib
import shutil
import sqlite3
import tempfile
from typing import Any, Callable, Concatenate, Iterator, ParamSpec, TypeVar

import sqlalchemy
from sqlalchemy import Engine, event
from sqlalchemy.orm import Session, sessionmaker

from lofi.log import LOGGER

from . import google_api

__all__ = ["Session", "connect", "get_url", "with_connection"]


_T = TypeVar("_T")
_P = ParamSpec("_P")


def create_engine(db_name: str) -> Engine:
    """Create SQLAlchemy engine."""
    engine = sqlalchemy.create_engine(get_url(db_name), poolclass=sqlalchemy.NullPool)

    def enable_foreign_keys(dbapi_connection: Any, connection_record: Any) -> None:  # noqa: ANN401, ARG001
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("pragma foreign_keys=on")
            cursor.close()

    event.listens_for(engine, "connect")(enable_foreign_keys)

    return engine


@contextlib.contextmanager
def connect(db_name: str = os.environ["DB_NAME"]) -> Iterator[Session]:
    """Connect to database."""
    with get_sessionmaker(db_name)() as session, session.begin():
        yield session


def download_local_db(
    drive_file_name: str = os.environ["DRIVE_DB_FILE"],
    db_path: pathlib.Path = pathlib.Path(os.environ["DB_NAME"]),
) -> None:
    LOGGER.info("Downloading compressed database")
    drive = google_api.get_google_drive_client()
    with get_temp_file_path() as zipped_path:
        google_api.download_file(drive, drive_file_name, zipped_path)
        with gzip.open(zipped_path, mode="rb") as in_file, db_path.open("wb") as out_file:
            LOGGER.info("Decompressing database")
            shutil.copyfileobj(in_file, out_file)
    LOGGER.info("Downloaded local database")


def get_sessionmaker(db_name: str) -> sessionmaker[Session]:
    """Return sessionmaker."""
    return sessionmaker(bind=create_engine(db_name))


@contextlib.contextmanager
def get_temp_file_path() -> Iterator[pathlib.Path]:
    with tempfile.NamedTemporaryFile(delete=False) as f:
        path = pathlib.Path(f.name)
    try:
        yield path
    finally:
        path.unlink(missing_ok=True)


def get_url(db_name: str) -> str:
    """Return database URL."""
    return f"sqlite:///{db_name}"


def upload_local_db(
    drive_file_name: str = os.environ["DRIVE_DB_FILE"],
    db_path: pathlib.Path = pathlib.Path(os.environ["DB_NAME"]),
) -> None:
    with get_temp_file_path() as zipped_path:
        with db_path.open("rb") as in_file, gzip.open(zipped_path, mode="wb") as out_file:
            LOGGER.info("Compressing database")
            shutil.copyfileobj(in_file, out_file)
        LOGGER.info("Uploading compressed database")
        drive = google_api.get_google_drive_client()
        google_api.upload_file(drive, drive_file_name, zipped_path)
    LOGGER.info("Uploaded local database")


def with_connection(func: Callable[Concatenate[Session, _P], _T]) -> Callable[_P, _T]:
    """Provide a database connection to a function."""

    @functools.wraps(func)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
        with connect() as session:
            return func(session, *args, **kwargs)

    return wrapper
