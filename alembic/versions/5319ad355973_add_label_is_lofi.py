"""add label.is_lofi

Revision ID: 5319ad355973
Revises: 8adb8a331f45
Create Date: 2023-08-29 10:27:13.760337

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5319ad355973"
down_revision = "8adb8a331f45"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "label",
        sa.Column(
            "is_lofi",
            sa.Boolean(),
            nullable=False,
            comment="Whether this label is a lofi label. "
            "If False, will not be included in stats reports and new lofi playlist.",
            server_default=sa.literal(True),
        ),
    )


def downgrade() -> None:
    op.drop_column("label", "is_lofi")
