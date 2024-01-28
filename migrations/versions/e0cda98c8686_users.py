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
down_revision: Union[str, None] = '22532f0c00dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True),
        sa.Column("discord_user_id", sa.VARCHAR(32), unique=True, nullable=False),
        sa.Column("discord_guild_id", sa.VARCHAR(32), nullable=True),
        sa.Column("discord_username", sa.VARCHAR(50), nullable=False),
        sa.Column("discord_nick", sa.VARCHAR(50), unique=True, nullable=False),
        sa.Column("guild_id", sa.Integer, sa.ForeignKey("guilds.id"), nullable=True, default=None),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now())
    )


def downgrade() -> None:
    op.drop_table("users")
