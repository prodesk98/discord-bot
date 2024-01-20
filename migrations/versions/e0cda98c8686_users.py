"""users

Revision ID: e0cda98c8686
Revises: 
Create Date: 2024-01-19 21:53:51.403059

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e0cda98c8686'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.INTEGER, primary_key=True, autoincrement=True, nullable=False, unique=True),
        sa.Column("discord_user_id", sa.VARCHAR(100), unique=True, nullable=False),
        sa.Column("discord_username", sa.VARCHAR(50), unique=True, nullable=False),
        sa.Column("received_initial_coins", sa.Boolean(True), default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now())
    )


def downgrade() -> None:
    op.drop_table("users")
