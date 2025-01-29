"""Add indexes on track.album_id and album.label_name.

Revision ID: 55c3b8dbf877
Revises: 69b27895941f
Create Date: 2025-01-29 17:55:48.136876

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "55c3b8dbf877"
down_revision = "69b27895941f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.get_bind().execute(sa.text("pragma foreign_keys = off"))

    with op.batch_alter_table("album", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_album_label_name"), ["label_name"], unique=False)

    with op.batch_alter_table("track", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_track_album_id"), ["album_id"], unique=False)

    op.get_bind().execute(sa.text("pragma foreign_keys = on"))


def downgrade() -> None:
    op.get_bind().execute(sa.text("pragma foreign_keys = off"))

    with op.batch_alter_table("track", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_track_album_id"))

    with op.batch_alter_table("album", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_album_label_name"))

    op.get_bind().execute(sa.text("pragma foreign_keys = on"))
