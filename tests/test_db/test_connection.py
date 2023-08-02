from collections import defaultdict
import contextlib
import functools
import pathlib
import tempfile
from typing import Iterator
from unittest.mock import patch

import boto3
import pytest

import lofi.db.connection


class PatchedS3Client:
    files: dict[tuple[str, str], bytes] = defaultdict(bytes)

    def download_file(self, bucket: str, key: str, filename: str) -> None:
        pathlib.Path(filename).write_bytes(self.files[bucket, key])

    def upload_file(self, filename: str, bucket: str, key: str) -> None:
        self.files[bucket, key] = pathlib.Path(filename).read_bytes()


@pytest.fixture
def patch_get_s3_client(monkeypatch: pytest.MonkeyPatch) -> PatchedS3Client:
    @functools.lru_cache
    def get_patched_s3_client() -> PatchedS3Client:
        return PatchedS3Client()

    @contextlib.contextmanager
    def patched() -> Iterator[PatchedS3Client]:
        yield get_patched_s3_client()

    monkeypatch.setattr(lofi.db.connection, "get_s3_client", patched)

    return get_patched_s3_client()


@pytest.mark.usefixtures("patch_get_s3_client")
def test_download_db_creates_and_deletes_afterwards() -> None:
    with lofi.db.connection.download_db("foo", "bar") as db_path:
        assert db_path.is_file()
    assert not db_path.is_file()


@pytest.mark.usefixtures("patch_get_s3_client")
def test_download_db_stores_updates() -> None:
    text = "foo"
    with lofi.db.connection.download_db("foo", "bar") as db_path:
        db_path.write_text(text)
    with lofi.db.connection.download_db("foo", "bar") as db_path:
        assert db_path.read_text() == text


@pytest.mark.usefixtures("patch_get_s3_client")
def test_connect_to_db() -> None:
    with lofi.db.connect("foo") as session:
        assert isinstance(session, lofi.db.Session)


def test_connect_to_db_uses_env_by_default(
    monkeypatch: pytest.MonkeyPatch, patch_get_s3_client: PatchedS3Client
) -> None:
    bucket_name = "foo"
    db_name = "bar"
    monkeypatch.setenv("AWS_BUCKET_NAME", bucket_name)
    monkeypatch.setenv("DB_NAME", db_name)
    with lofi.db.connect():
        pass
    assert patch_get_s3_client.files[bucket_name, db_name] != b""


def test_get_s3_client() -> None:
    f = tempfile.TemporaryFile()
    with patch.object(boto3, "client", return_value=f) as mock:
        with lofi.db.connection.get_s3_client():
            assert not f.closed
        assert f.closed
        mock.assert_called_once_with("s3")
