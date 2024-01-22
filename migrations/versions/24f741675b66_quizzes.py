"""quizzes

Revision ID: 24f741675b66
Revises: 089c71ee9a92
Create Date: 2024-01-20 10:58:04.172454

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '24f741675b66'
down_revision: Union[str, None] = '089c71ee9a92'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "quizzes",
        sa.Column("id", sa.Integer, unique=True, autoincrement=True, primary_key=True),
        sa.Column("status", sa.Integer, default=0),
        sa.Column("amount", sa.Float, default=0),
        sa.Column("theme", sa.String(100), nullable=False),
        sa.Column("question", sa.String(100), nullable=False),
        sa.Column("alternatives", sa.JSON),
        sa.Column("truth", sa.Integer, default=-1, nullable=False),
        sa.Column("voice_url", sa.String(256), nullable=True, default=None),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now())
    )


def downgrade() -> None:
    op.drop_table("quizzes")
