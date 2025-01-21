"""add tables.

Revision ID: 34f171ff838a
Revises:
Create Date: 2023-08-03 12:14:31.693243

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "34f171ff838a"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "artist",
        sa.Column("id", sa.String(), nullable=False, comment="Spotify artist ID"),
        sa.Column("name", sa.String(), nullable=False, comment="Name of the artist"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_artist")),
    )
    op.create_table(
        "playlist",
        sa.Column("id", sa.String(), nullable=False, comment="Spotify playlist ID"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_playlist")),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.String(), nullable=False, comment="Spotify user ID"),
        sa.Column("token", sa.String(), nullable=True, comment="Spotipy cached token."),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user")),
    )
    op.create_table(
        "label",
        sa.Column(
            "name",
            sa.String(),
            nullable=False,
            comment="Name of the record label",
        ),
        sa.Column(
            "playlist_id",
            sa.String(),
            nullable=False,
            comment="Spotify ID of the playlist containing label releases.",
        ),
        sa.ForeignKeyConstraint(
            ["playlist_id"],
            ["playlist.id"],
            name=op.f("fk_label_playlist_id_playlist"),
        ),
        sa.PrimaryKeyConstraint("name", name=op.f("pk_label")),
    )
    op.create_table(
        "album",
        sa.Column("id", sa.String(), nullable=False, comment="Spotify album ID"),
        sa.Column(
            "label_name",
            sa.String(),
            nullable=False,
            comment="Name of the record label of the album",
        ),
        sa.Column("name", sa.String(), nullable=False, comment="Name of the album"),
        sa.Column(
            "release_date",
            sa.Date(),
            nullable=False,
            comment="Release date of the album",
        ),
        sa.Column(
            "type",
            sa.Enum("album", "compilation", "single", name="albumtype"),
            nullable=False,
            comment="Type of the album ('album', 'compilation', or 'single')",
        ),
        sa.ForeignKeyConstraint(
            ["label_name"],
            ["label.name"],
            name=op.f("fk_album_label_name_label"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_album")),
    )
    op.create_table(
        "album_popularity",
        sa.Column("album_id", sa.String(), nullable=False, comment="Spotify album ID"),
        sa.Column(
            "date",
            sa.Date(),
            nullable=False,
            comment="Date at which popularity was collected",
        ),
        sa.Column("Spotify popularity", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["album_id"],
            ["album.id"],
            name=op.f("fk_album_popularity_album_id_album"),
        ),
        sa.PrimaryKeyConstraint("album_id", "date", name=op.f("pk_album_popularity")),
    )
    op.create_table(
        "rel_artist_album",
        sa.Column("album_id", sa.String(), nullable=False, comment="Spotify album ID"),
        sa.Column(
            "artist_id",
            sa.String(),
            nullable=False,
            comment="Spotify artist ID",
        ),
        sa.Column(
            "artist_position",
            sa.Integer(),
            nullable=False,
            comment="Position of the artist in the list of all artists of the album",
        ),
        sa.ForeignKeyConstraint(
            ["album_id"],
            ["album.id"],
            name=op.f("fk_rel_artist_album_album_id_album"),
        ),
        sa.ForeignKeyConstraint(
            ["artist_id"],
            ["artist.id"],
            name=op.f("fk_rel_artist_album_artist_id_artist"),
        ),
        sa.PrimaryKeyConstraint(
            "album_id",
            "artist_id",
            "artist_position",
            name=op.f("pk_rel_artist_album"),
        ),
    )
    op.create_table(
        "track",
        sa.Column("id", sa.String(), nullable=False, comment="Spotify track ID"),
        sa.Column(
            "album_id",
            sa.String(),
            nullable=False,
            comment="Spotify ID of the album of the track",
        ),
        sa.Column("isrc", sa.String(), nullable=False, comment="ISRC of the track"),
        sa.Column("name", sa.String(), nullable=False, comment="Name of the track"),
        sa.Column(
            "position",
            sa.Integer(),
            nullable=False,
            comment="Position of the track within its album",
        ),
        sa.ForeignKeyConstraint(
            ["album_id"],
            ["album.id"],
            name=op.f("fk_track_album_id_album"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_track")),
    )
    op.create_table(
        "rel_artist_track",
        sa.Column("track_id", sa.String(), nullable=False, comment="Spotify track ID"),
        sa.Column(
            "artist_id",
            sa.String(),
            nullable=False,
            comment="Spotify artist ID",
        ),
        sa.Column(
            "artist_position",
            sa.Integer(),
            nullable=False,
            comment="Position of the artist in the list of all artists of the album",
        ),
        sa.ForeignKeyConstraint(
            ["artist_id"],
            ["artist.id"],
            name=op.f("fk_rel_artist_track_artist_id_artist"),
        ),
        sa.ForeignKeyConstraint(
            ["track_id"],
            ["track.id"],
            name=op.f("fk_rel_artist_track_track_id_track"),
        ),
        sa.PrimaryKeyConstraint(
            "track_id",
            "artist_id",
            "artist_position",
            name=op.f("pk_rel_artist_track"),
        ),
    )
    op.create_table(
        "track_popularity",
        sa.Column("track_id", sa.String(), nullable=False, comment="Spotify track ID"),
        sa.Column(
            "date",
            sa.Date(),
            nullable=False,
            comment="Date at which popularity was collected",
        ),
        sa.Column("Spotify popularity", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["track_id"],
            ["track.id"],
            name=op.f("fk_track_popularity_track_id_track"),
        ),
        sa.PrimaryKeyConstraint("track_id", "date", name=op.f("pk_track_popularity")),
    )


def downgrade() -> None:
    op.drop_table("track_popularity")
    op.drop_table("rel_artist_track")
    op.drop_table("track")
    op.drop_table("rel_artist_album")
    op.drop_table("album_popularity")
    op.drop_table("album")
    op.drop_table("label")
    op.drop_table("user")
    op.drop_table("playlist")
    op.drop_table("artist")
