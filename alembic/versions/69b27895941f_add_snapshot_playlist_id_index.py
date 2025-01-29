"""Add Snapshot.playlist_id index.

Revision ID: 69b27895941f
Revises: bf18360a3ed8
Create Date: 2025-01-29 17:26:52.559995

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "69b27895941f"
down_revision = "bf18360a3ed8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.get_bind().execute(sa.text("pragma foreign_keys = off"))

    with op.batch_alter_table("snapshot", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_snapshot_playlist_id"), ["playlist_id"], unique=False)

    op.get_bind().execute(sa.text("pragma foreign_keys = on"))


def downgrade() -> None:
    op.get_bind().execute(sa.text("pragma foreign_keys = off"))

    with op.batch_alter_table("snapshot", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_snapshot_playlist_id"))

    op.get_bind().execute(sa.text("pragma foreign_keys = on"))
