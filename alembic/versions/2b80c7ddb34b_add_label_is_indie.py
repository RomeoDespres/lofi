"""add label.is_indie

Revision ID: 2b80c7ddb34b
Revises: 5319ad355973
Create Date: 2023-08-31 13:06:57.457292

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "2b80c7ddb34b"
down_revision = "5319ad355973"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.get_bind().execute(sa.text("pragma foreign_keys = off"))
    with op.batch_alter_table("label") as batch_op:
        batch_op.add_column(
            sa.Column(
                "is_indie",
                sa.Boolean(),
                nullable=False,
                server_default=sa.literal(False),
                comment="Whether this label is independent from tracked labels.",
            )
        )
    with op.batch_alter_table("label") as batch_op:
        batch_op.alter_column("is_indie", server_default=None)
    op.get_bind().execute(sa.text("pragma foreign_keys = on"))


def downgrade() -> None:
    op.drop_column("label", "is_indie")
