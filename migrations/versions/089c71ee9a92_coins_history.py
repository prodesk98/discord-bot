"""coins_history

Revision ID: 089c71ee9a92
Revises: e0cda98c8686
Create Date: 2024-01-20 10:39:06.492121

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '089c71ee9a92'
down_revision: Union[str, None] = '157a2a1c3b2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "coins_history",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("amount", sa.Integer),
        sa.Column("description", sa.String(155), nullable=True, default=None),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("coins_history")
