import contextlib
import pathlib
import tempfile
from typing import Iterator

import boto3
from mypy_boto3_s3 import S3Client
import sqlalchemy
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from .. import env


__all__ = ["Session", "download_db", "connect", "get_s3_client"]


def create_engine(db_name: str) -> Engine:
    """Create SQLAlchemy engine."""
    return sqlalchemy.create_engine(get_url(db_name), poolclass=sqlalchemy.NullPool)


@contextlib.contextmanager
def connect(db_name: str | None = None) -> Iterator[Session]:
    """Connect to database."""
    if db_name is None:
        db_name = env.db_name()
    with (
        download_db(env.aws_bucket_name(), env.db_name()) as db_path,
        get_sessionmaker(str(db_path))() as session,
        session.begin(),
    ):
        yield session


@contextlib.contextmanager
def download_db(bucket_name: str, db_name: str) -> Iterator[pathlib.Path]:
    with tempfile.NamedTemporaryFile(delete=False) as f:
        path = pathlib.Path(f.name)
    try:
        with get_s3_client() as s3:
            s3.download_file(bucket_name, db_name, str(path))
            yield path
            s3.upload_file(str(path), bucket_name, db_name)
    finally:
        path.unlink(missing_ok=True)


@contextlib.contextmanager
def get_s3_client() -> Iterator[S3Client]:
    with contextlib.closing(boto3.client("s3")) as s3:
        yield s3


def get_url(db_name: str) -> str:
    """Return database URL."""
    return f"sqlite:///{db_name}"


def get_sessionmaker(db_name: str) -> sessionmaker[Session]:
    """Return sessionmaker."""
    return sessionmaker(bind=create_engine(db_name))
