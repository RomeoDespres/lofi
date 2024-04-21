import pathlib
import tempfile
from unittest.mock import patch

import boto3
import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError

import lofi.db.connection
from tests.conftest import PatchedS3Client


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
def test_download_db_twice_returns_same_file() -> None:
    with (
        lofi.db.connection.download_db("foo", "bar") as db_path_1,
        lofi.db.connection.download_db("foo", "bar") as db_path_2,
    ):
        assert db_path_1 == db_path_2


@pytest.mark.usefixtures("patch_get_s3_client")
def test_download_and_upload_local_db(monkeypatch: pytest.MonkeyPatch) -> None:
    text_1, text_2 = "foo", "bar"

    # Download DB from patched S3 client and write text_1
    with lofi.db.connection.download_db() as db_path:
        db_path.write_text(text_1)

    # Generate local DB file name
    with tempfile.NamedTemporaryFile() as f:
        path = pathlib.Path(f.name)

    # For now our file has been deleted by the NamedTemporaryFile
    assert not path.exists()
    monkeypatch.setenv("LOCAL_DB", str(path))

    # Download to local DB
    lofi.db.download_local_db()

    # Now our file should contain text_1
    assert path.exists()
    with lofi.db.connection.download_db() as db_path:
        assert db_path.read_text() == text_1

        # Now let's write text_2 and see if it is uploaded correctly
        db_path.write_text(text_2)
    assert path.read_text() == text_2
    lofi.db.upload_local_db()

    # Download DB from patched S3 client and check it contains text_2
    monkeypatch.delenv("LOCAL_DB")
    with lofi.db.connection.download_db() as db_path:
        assert db_path.read_text() == text_2


@pytest.mark.usefixtures("patch_get_s3_client")
def test_connect_to_db() -> None:
    with lofi.db.connect("foo") as session:
        assert isinstance(session, lofi.db.Session)


@pytest.mark.usefixtures("patch_get_s3_client")
def test_connect_to_db_enables_foreign_keys() -> None:
    with lofi.db.connect() as session:
        session.execute(text("create table t1(a int primary key)"))
        session.execute(
            text("create table t2(a int primary key, foreign key (a) references t1(a))"),
        )
        with pytest.raises(IntegrityError):
            session.execute(text("insert into t2(a) values (1)"))


@pytest.mark.usefixtures("patch_get_s3_client")
def test_connect_to_db_twice() -> None:
    with lofi.db.connect() as session_1:
        with pytest.raises(OperationalError):
            session_1.execute(text("select * from t"))
        with lofi.db.connect() as session_2:
            session_2.execute(text("create table t(a int primary key)"))
        with lofi.db.connect() as session_2:
            session_2.execute(text("select * from t"))
    with lofi.db.connect() as session_1:
        session_1.execute(text("select * from t"))


def test_connect_to_db_uses_env_by_default(
    monkeypatch: pytest.MonkeyPatch,
    patch_get_s3_client: PatchedS3Client,
) -> None:
    bucket_name = "foo"
    db_name = "bar"
    monkeypatch.setenv("AWS_BUCKET_NAME", bucket_name)
    monkeypatch.setenv("DB_NAME", db_name)
    with lofi.db.connect() as session:
        session.execute(text("create table t(c int)"))
    assert patch_get_s3_client.files[bucket_name, db_name] != b""


@pytest.mark.usefixtures("patch_get_s3_client")
def test_connect_to_db_uses_local_db_if_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with tempfile.NamedTemporaryFile() as f:
        path = pathlib.Path(f.name)
    assert not path.exists()
    monkeypatch.setenv("LOCAL_DB", str(path))
    with lofi.db.connect() as session:
        # Run something to ensure engine actually connects
        session.execute(text("create table t(c int)"))
    assert path.is_file()
    path.unlink()


def test_get_s3_client() -> None:
    f = tempfile.TemporaryFile()
    with patch.object(boto3, "client", return_value=f) as mock:
        with lofi.db.connection.get_s3_client():
            assert not f.closed
        assert f.closed
        mock.assert_called_once_with("s3")


@pytest.mark.usefixtures("patch_get_s3_client")
def test_with_connection() -> None:
    @lofi.db.with_connection
    def foo(session: lofi.db.Session) -> None:
        assert isinstance(session, lofi.db.Session)

    foo()
