"""quiz_bet

Revision ID: 5ddd0f19e259
Revises: 056fa30634e8
Create Date: 2024-01-24 21:08:31.267550

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from models import QuizEnumChoices

# revision identifiers, used by Alembic.
revision: str = '5ddd0f19e259'
down_revision: Union[str, None] = '24f741675b66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "quiz_bet",
        sa.Column("id", sa.Integer, unique=True, autoincrement=True, primary_key=True),
        sa.Column("quiz_id", sa.Integer, sa.ForeignKey("quizzes.id")),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("amount", sa.Integer, default=0),
        sa.Column("choice", sa.Enum(QuizEnumChoices), default=1),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now())
    )


def downgrade() -> None:
    op.drop_table("quiz_bet")
