"""add snapshot table.

Revision ID: 8adb8a331f45
Revises: 34f171ff838a
Create Date: 2023-08-04 11:11:15.398319

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "8adb8a331f45"
down_revision = "34f171ff838a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "snapshot",
        sa.Column(
            "id", sa.String(), nullable=False, comment="Spotify playlist snapshot ID",
        ),
        sa.Column(
            "position",
            sa.Integer(),
            nullable=False,
            comment="Track position within playlist",
        ),
        sa.Column("track_id", sa.String(), nullable=False, comment="Spotify track ID"),
        sa.PrimaryKeyConstraint("id", "position", name=op.f("pk_snapshot")),
    )


def downgrade() -> None:
    op.drop_table("snapshot")
