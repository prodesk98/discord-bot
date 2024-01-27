"""pets

Revision ID: 157a2a1c3b2b
Revises: 6d0fc90adf37
Create Date: 2024-01-26 21:32:27.691515

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '157a2a1c3b2b'
down_revision: Union[str, None] = '6d0fc90adf37'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pets",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("config_pet_id", sa.Integer),
        sa.Column("name", sa.String(155)),
        sa.Column("personality", sa.String(350)),
        sa.Column("swear_words", sa.JSON),
        sa.Column("informal_greeting", sa.JSON),
        sa.Column("level", sa.Integer),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("pets")
