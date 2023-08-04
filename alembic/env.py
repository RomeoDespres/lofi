from contextlib import nullcontext
from logging.config import fileConfig
from typing import ContextManager

from alembic import context

from lofi import db
from lofi.db.models import Base


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_online() -> None:
    if (session := config.attributes.get("session")) is None:  # pragma: no cover
        cm: ContextManager[db.Session] = db.connect()
    else:
        assert isinstance(session, db.Session)
        cm = nullcontext(session)
    with cm as session:
        context.configure(
            connection=session.connection(), target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
