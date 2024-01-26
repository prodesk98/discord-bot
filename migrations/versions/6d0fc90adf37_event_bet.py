"""event_bet

Revision ID: 6d0fc90adf37
Revises: 5ddd0f19e259
Create Date: 2024-01-24 21:08:50.626836

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from models import BettingEnumChoices

# revision identifiers, used by Alembic.
revision: str = '6d0fc90adf37'
down_revision: Union[str, None] = '5ddd0f19e259'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'event_bet',
        sa.Column("id", sa.Integer, unique=True, autoincrement=True, primary_key=True),
        sa.Column("event_id", sa.Integer, sa.ForeignKey("betting_events.id")),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("amount", sa.Integer, default=0),
        sa.Column("choice", sa.Enum(BettingEnumChoices), default=1),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now())
    )


def downgrade() -> None:
    op.drop_table("event_bet")
