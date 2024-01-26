"""betting_events

Revision ID: 056fa30634e8
Revises: dd1d47ac6043
Create Date: 2024-01-24 00:39:14.017268

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from models import BettingEnumStatus

# revision identifiers, used by Alembic.
revision: str = '056fa30634e8'
down_revision: Union[str, None] = 'dd1d47ac6043'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "betting_events",
        sa.Column("id", sa.Integer, unique=True, autoincrement=True, primary_key=True),
        sa.Column("winner_choice_id", sa.Integer, nullable=True, default=None),
        sa.Column("name", sa.String(255)),
        sa.Column("status", sa.Enum(BettingEnumStatus), default=1),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now())
    )


def downgrade() -> None:
    op.drop_table("betting_events")
