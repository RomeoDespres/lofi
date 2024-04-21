"""add label playlist image.

Revision ID: 7a960d8298ac
Revises: fcba2a965e33
Create Date: 2024-01-07 16:57:18.516815

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "7a960d8298ac"
down_revision = "fcba2a965e33"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "label",
        sa.Column(
            "playlist_image_url",
            sa.String(),
            nullable=True,
            comment="Cover image URL of the playlist containing label releases.",
        ),
    )


def downgrade() -> None:
    op.drop_column("label", "playlist_image_url")
