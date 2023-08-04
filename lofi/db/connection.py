import contextlib
import functools
import pathlib
import sqlite3
import tempfile
from typing import (
    Any,
    Callable,
    Concatenate,
    Generic,
    Iterator,
    ParamSpec,
    Protocol,
    TypeVar,
)

import boto3
from mypy_boto3_s3 import S3Client
import sqlalchemy
from sqlalchemy import Engine, event
from sqlalchemy.orm import Session, sessionmaker

from .. import env


__all__ = [
    "Session",
    "download_db",
    "connect",
    "get_s3_client",
    "get_url",
    "with_connection",
]


_T = TypeVar("_T")
_Cov = TypeVar("_Cov", covariant=True)
_P = ParamSpec("_P")


class TempFileManager:
    def __init__(self) -> None:
        self.current_count = 0
        self.current_path: pathlib.Path | None = None

    @contextlib.contextmanager
    def get_temp_file(self, bucket_name: str, db_name: str) -> Iterator[pathlib.Path]:
        if self.current_count == 0:
            assert self.current_path is None
            with tempfile.NamedTemporaryFile(delete=False) as f:
                self.current_path = pathlib.Path(f.name)
            with get_s3_client() as s3:
                s3.download_file(bucket_name, db_name, str(self.current_path))
        assert self.current_path is not None
        self.current_count += 1
        try:
            yield self.current_path
        finally:
            self.current_count -= 1
            if self.current_count == 0:
                with get_s3_client() as s3:
                    s3.upload_file(str(self.current_path), bucket_name, db_name)
                self.current_path.unlink()
                self.current_path = None


class InjectedBucketAndDbName(Protocol, Generic[_Cov]):
    def __call__(
        self, bucket_name: str | None = None, db_name: str | None = None
    ) -> _Cov:  # pragma: no cover
        ...


def inject_bucket_and_db_name_from_env(
    func: Callable[[str, str], _Cov]
) -> InjectedBucketAndDbName[_Cov]:
    @functools.wraps(func)
    def wrapped(bucket_name: str | None = None, db_name: str | None = None) -> _Cov:
        if bucket_name is None:
            bucket_name = env.aws_bucket_name()
        if db_name is None:
            db_name = env.db_name()
        return func(bucket_name, db_name)

    return wrapped


def create_engine(db_name: str) -> Engine:
    """Create SQLAlchemy engine."""
    engine = sqlalchemy.create_engine(get_url(db_name), poolclass=sqlalchemy.NullPool)

    def enable_foreign_keys(dbapi_connection: Any, connection_record: Any) -> None:
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("pragma foreign_keys=on")
            cursor.close()

    event.listens_for(engine, "connect")(enable_foreign_keys)

    return engine


@contextlib.contextmanager
def connect(db_name: str | None = None) -> Iterator[Session]:
    """Connect to database."""
    if db_name is None:
        db_name = env.db_name()
    with (
        download_db() as db_path,
        get_sessionmaker(str(db_path))() as session,
        session.begin(),
    ):
        yield session


@contextlib.contextmanager
@inject_bucket_and_db_name_from_env
def download_db(bucket_name: str, db_name: str) -> Iterator[pathlib.Path]:
    try:
        # Do not download and use local file instead. Useful for development.
        yield env.local_db()
        return
    except KeyError:
        pass
    with get_temp_file_manager().get_temp_file(bucket_name, db_name) as path:
        yield path


@inject_bucket_and_db_name_from_env
def download_local_db(bucket_name: str, db_name: str) -> None:
    with get_s3_client() as s3:
        s3.download_file(bucket_name, db_name, str(env.local_db()))


@contextlib.contextmanager
def get_s3_client() -> Iterator[S3Client]:
    with contextlib.closing(boto3.client("s3")) as s3:
        yield s3


def get_sessionmaker(db_name: str) -> sessionmaker[Session]:
    """Return sessionmaker."""
    return sessionmaker(bind=create_engine(db_name))


@functools.lru_cache()
def get_temp_file_manager() -> TempFileManager:
    return TempFileManager()


def get_url(db_name: str) -> str:
    """Return database URL."""
    return f"sqlite:///{db_name}"


@inject_bucket_and_db_name_from_env
def upload_local_db(bucket_name: str, db_name: str) -> None:
    with get_s3_client() as s3:
        s3.upload_file(str(env.local_db()), bucket_name, db_name)


def with_connection(func: Callable[Concatenate[Session, _P], _T]) -> Callable[_P, _T]:
    """Decorator to provide a database connection to a function."""

    @functools.wraps(func)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
        with connect() as session:
            return func(session, *args, **kwargs)

    return wrapper
