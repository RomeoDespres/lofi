from lofi import db
from tests.conftest import run_alembic_migrations


def test_alembic_migrations(session: db.Session) -> None:
    run_alembic_migrations(session, "downgrade")
    run_alembic_migrations(session, "upgrade")
