"""add editorial playlists

Revision ID: 73619481350c
Revises: 7a960d8298ac
Create Date: 2024-01-11 09:17:16.879579

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "73619481350c"
down_revision = "7a960d8298ac"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.get_bind().execute(sa.text("pragma foreign_keys = off"))

    # Transfer image URLs from label table to playlist table
    op.add_column(
        "playlist",
        sa.Column(
            "image_url",
            sa.String(),
            nullable=True,
            comment="Cover image URL of the playlist",
        ),
    )
    label_table = sa.table(
        "label", sa.column("playlist_id"), sa.column("playlist_image_url")
    )
    playlist_table = sa.table("playlist", sa.column("id"), sa.column("image_url"))
    update_playlist_sql = sa.update(playlist_table).values(
        image_url=sa.select(label_table.c.playlist_image_url)
        .where(label_table.c.playlist_id == playlist_table.c.id)
        .scalar_subquery()
    )
    op.get_bind().execute(update_playlist_sql)
    op.drop_column("label", "playlist_image_url")

    op.add_column(
        "snapshot",
        sa.Column(
            "timestamp",
            sa.DateTime(),
            comment="Timestamp at which snapshot was captured. "
            "NULL for historical values where it wasn't recorded",
            nullable=True,
        ),
    )
    op.create_index(
        op.f("ix_snapshot_track_id"), "snapshot", ["track_id"], unique=False
    )

    op.add_column(
        "playlist",
        sa.Column(
            "is_editorial",
            sa.Boolean(),
            comment="Whether playlist is a Spotify editorial playlist",
            nullable=False,
            server_default=sa.literal(False),
        ),
    )
    with op.batch_alter_table("playlist") as batch_op:
        batch_op.alter_column("is_editorial", server_default=None)

    # Fix a typo
    with op.batch_alter_table("track_popularity") as batch_op:
        batch_op.alter_column(
            "Spotify popularity",
            new_column_name="popularity",
            comment="Spotify popularity",
        )

    op.get_bind().execute(sa.text("pragma foreign_keys = on"))


def downgrade() -> None:
    op.get_bind().execute(sa.text("pragma foreign_keys = off"))

    with op.batch_alter_table("track_popularity") as batch_op:
        batch_op.alter_column(
            "popularity",
            new_column_name="Spotify popularity",
            comment=None,
        )

    op.drop_column("playlist", "is_editorial")

    op.drop_index(op.f("ix_snapshot_track_id"), "snapshot")
    op.drop_column("snapshot", "timestamp")

    op.add_column("label", sa.Column("playlist_image_url", sa.VARCHAR(), nullable=True))
    label_table = sa.table(
        "label", sa.column("playlist_id"), sa.column("playlist_image_url")
    )
    playlist_table = sa.table("playlist", sa.column("id"), sa.column("image_url"))
    update_label_sql = sa.update(label_table).values(
        playlist_image_url=sa.select(playlist_table.c.image_url)
        .where(playlist_table.c.id == label_table.c.playlist_id)
        .scalar_subquery()
    )
    op.get_bind().execute(update_label_sql)
    op.drop_column("playlist", "image_url")

    op.get_bind().execute(sa.text("pragma foreign_keys = on"))
