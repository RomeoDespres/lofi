
import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

import lofi.db.connection


@pytest.mark.usefixtures("_patch_connect")
def test_connect_to_db_enables_foreign_keys() -> None:
    with lofi.db.connect() as session:
        session.execute(text("create table t1(a int primary key)"))
        session.execute(
            text("create table t2(a int primary key, foreign key (a) references t1(a))"),
        )
        with pytest.raises(IntegrityError):
            session.execute(text("insert into t2(a) values (1)"))


@pytest.mark.usefixtures("_patch_connect")
def test_with_connection() -> None:
    @lofi.db.with_connection
    def foo(session: lofi.db.Session) -> None:
        assert isinstance(session, lofi.db.Session)

    foo()
