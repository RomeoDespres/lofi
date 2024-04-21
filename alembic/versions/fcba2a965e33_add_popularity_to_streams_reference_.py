"""add popularity to streams reference table.

Revision ID: fcba2a965e33
Revises: 2b80c7ddb34b
Create Date: 2024-01-06 13:54:14.003215

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "fcba2a965e33"
down_revision = "2b80c7ddb34b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "popularity_streams",
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("popularity", sa.Integer(), nullable=False),
        sa.Column("streams_q1", sa.BigInteger(), nullable=False),
        sa.Column("streams_q2", sa.BigInteger(), nullable=False),
        sa.Column("streams_q3", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint(
            "date", "popularity", name=op.f("pk_popularity_streams"),
        ),
    )


def downgrade() -> None:
    op.drop_table("popularity_streams")
