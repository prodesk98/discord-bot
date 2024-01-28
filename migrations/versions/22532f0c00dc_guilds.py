"""guilds

Revision ID: 22532f0c00dc
Revises: 5ddd0f19e259
Create Date: 2024-01-28 03:15:07.823847

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '22532f0c00dc'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "guilds",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True),
        sa.Column("name", sa.String(155), nullable=False),
        sa.Column("emoji", sa.String(32), nullable=False)
    )


def downgrade() -> None:
    op.drop_table("guilds")
