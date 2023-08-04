from collections import defaultdict
import contextlib
import pathlib
from typing import Iterator, Literal

import alembic.command
import alembic.config
import pytest

from lofi import db
from lofi import log
import lofi.db.connection
import lofi.etl.log
import lofi.spotify_api.log


class PatchedS3Client:
    """Patched S3 client for testing purposes.

    Files can be uploaded and downloaded into a memory cache
    with the same API as `boto3.client("s3")`.
    """

    def __init__(self) -> None:
        self.files: dict[tuple[str, str], bytes] = defaultdict(bytes)

    def download_file(self, bucket: str, key: str, filename: str) -> None:
        """Download file from memory cache into `filename`.

        Parameters
        ----------
        bucket
            Emulated S3 bucket name.
        key
            Emulated S3 file name.
        filename
            Name of the file to download into.
        """
        pathlib.Path(filename).write_bytes(self.files[bucket, key])

    def upload_file(self, filename: str, bucket: str, key: str) -> None:
        """Upload file from `filename` to memory cache.

        Parameters
        ----------
        filename
            Name of the file to upload into emulated S3 bucket.
        bucket
            Emulated S3 bucket name.
        key
            Emulated S3 file name.
        """
        self.files[bucket, key] = pathlib.Path(filename).read_bytes()


def load_data(session: db.Session, *objs: db.Base) -> None:
    """Load data models into database.

    Parameters
    ----------
    session
        Connected SQLAlchemy session.
    *objs
        SQLAlchemy objects to load.
    """
    session.add_all(objs)
    session.flush()


@pytest.fixture(autouse=True)
def no_local_db(monkeypatch: pytest.MonkeyPatch) -> None:
    """Temporarily delete the `LOCAL_DB` environement variable.

    Prevents overwriting the true local db when testing during
    local development.
    """
    monkeypatch.delenv("LOCAL_DB", raising=False)


@pytest.fixture(autouse=True)
def no_spotify_user_id(monkeypatch: pytest.MonkeyPatch) -> None:
    """Temporarily delete the `SPOTIFY_USER_ID` environement variable.

    Prevents unwanted API calls against a true Spotify profile.
    """
    monkeypatch.delenv("SPOTIFY_USER_ID", raising=False)


@pytest.fixture
def patch_get_s3_client(monkeypatch: pytest.MonkeyPatch) -> PatchedS3Client:
    """Patch `lofi` to use `PatchedS3Client` instead of boto3.

    Returns
    -------
    PatchedS3Client instance.
    """
    s3_client = PatchedS3Client()

    @contextlib.contextmanager
    def patched() -> Iterator[PatchedS3Client]:
        yield s3_client

    monkeypatch.setattr(lofi.db.connection, "get_s3_client", patched)

    return s3_client


@pytest.fixture(autouse=True)
def patch_loggers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(lofi.etl.log, "LOGGER", log.get_logger("lofi:test:etl"))
    monkeypatch.setattr(
        lofi.spotify_api.log, "LOGGER", log.get_logger("lofi:test:spotify_api")
    )


def run_alembic_migrations(
    session: db.Session, type: Literal["upgrade", "downgrade"] = "upgrade"
) -> None:
    """Upgrade temp DB to latest Alembic version."""
    config_path = pathlib.Path(__file__).parent.parent / "alembic.ini"
    config = alembic.config.Config(str(config_path))
    config.attributes["session"] = session
    # config.set_main_option("sqlalchemy.url", db.get_url())
    if type == "upgrade":
        alembic.command.upgrade(config, "head")
    elif type == "downgrade":
        alembic.command.downgrade(config, "base")
    else:
        raise ValueError(
            f"`type` must be 'upgrade' or 'downgrade', received {repr(type)}"
        )


@pytest.fixture
def session(patch_get_s3_client: PatchedS3Client) -> Iterator[db.Session]:
    """Yield a SQLAlchemy session connected to a test database.

    Session is rolled back on exit.

    Yields
    ------
    Connected SQLAlchemy session.
    """
    with db.connect() as session:
        run_alembic_migrations(session, "upgrade")
        yield session
        session.rollback()
