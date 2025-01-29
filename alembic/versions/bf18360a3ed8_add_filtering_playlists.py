"""Add filtering playlists.

Revision ID: bf18360a3ed8
Revises: ffad2d23c8ad
Create Date: 2025-01-29 16:22:46.021753

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "bf18360a3ed8"
down_revision = "ffad2d23c8ad"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.get_bind().execute(sa.text("pragma foreign_keys = off"))

    with op.batch_alter_table("playlist", schema=None) as batch_op:
        batch_op.add_column(sa.Column("filter_for_label_name", sa.String(), nullable=True))
        batch_op.create_foreign_key(
            batch_op.f("fk_playlist_filter_for_label_name_label"), "label", ["filter_for_label_name"], ["name"]
        )

    with op.batch_alter_table("track", schema=None) as batch_op:
        batch_op.add_column(sa.Column("is_lofi", sa.Boolean(), server_default=sa.text("1"), nullable=False))

    op.get_bind().execute(sa.text("pragma foreign_keys = on"))


def downgrade() -> None:
    op.get_bind().execute(sa.text("pragma foreign_keys = off"))

    with op.batch_alter_table("track", schema=None) as batch_op:
        batch_op.drop_column("is_lofi")

    with op.batch_alter_table("playlist", schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f("fk_playlist_filter_for_label_name_label"), type_="foreignkey")
        batch_op.drop_column("filter_for_label_name")

    op.get_bind().execute(sa.text("pragma foreign_keys = on"))
