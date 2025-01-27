"""Add album images.

Revision ID: ffad2d23c8ad
Revises: 98eebf462d75
Create Date: 2025-01-27 23:15:03.695363

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "ffad2d23c8ad"
down_revision = "98eebf462d75"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.get_bind().execute(sa.text("pragma foreign_keys = off"))

    with op.batch_alter_table("album", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("image_url_s", sa.String(), nullable=True, comment="Spotify album cover URL (small size)")
        )
        batch_op.add_column(
            sa.Column("image_url_l", sa.String(), nullable=True, comment="Spotify album cover URL (large size)")
        )

    op.get_bind().execute(sa.text("pragma foreign_keys = on"))


def downgrade() -> None:
    op.get_bind().execute(sa.text("pragma foreign_keys = off"))

    with op.batch_alter_table("album", schema=None) as batch_op:
        batch_op.drop_column("image_url_s")
        batch_op.drop_column("image_url_l")

    op.get_bind().execute(sa.text("pragma foreign_keys = on"))
