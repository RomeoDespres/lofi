"""add snapshot-playlist relationship

Revision ID: 4b7adbd648dc
Revises: 73619481350c
Create Date: 2024-01-11 11:03:04.383732

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4b7adbd648dc"
down_revision = "73619481350c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("snapshot", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "playlist_id",
                sa.String(),
                nullable=True,
                comment="Id of this snapshot's playlist. "
                "NULL for historical values where it wasn't recorded",
            )
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_snapshot_playlist_id_playlist"),
            "playlist",
            ["playlist_id"],
            ["id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("snapshot", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_snapshot_playlist_id_playlist"), type_="foreignkey"
        )
        batch_op.drop_column("playlist_id")
