"""Add artist image.

Revision ID: 98eebf462d75
Revises: 4b7adbd648dc
Create Date: 2025-01-27 15:41:49.951594

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "98eebf462d75"
down_revision = "4b7adbd648dc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.get_bind().execute(sa.text("pragma foreign_keys = off"))

    with op.batch_alter_table("artist", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "image_url_s", sa.String(), nullable=True, comment="Spotify artist profile picture URL (small size)"
            )
        )
        batch_op.add_column(
            sa.Column(
                "image_url_l", sa.String(), nullable=True, comment="Spotify artist profile picture URL (large size)"
            )
        )

    op.get_bind().execute(sa.text("pragma foreign_keys = on"))


def downgrade() -> None:
    op.get_bind().execute(sa.text("pragma foreign_keys = off"))

    with op.batch_alter_table("artist", schema=None) as batch_op:
        batch_op.drop_column("image_url")

    op.get_bind().execute(sa.text("pragma foreign_keys = on"))
