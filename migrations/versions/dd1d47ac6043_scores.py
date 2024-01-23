"""score

Revision ID: dd1d47ac6043
Revises: 24f741675b66
Create Date: 2024-01-23 01:15:07.618031

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dd1d47ac6043'
down_revision: Union[str, None] = '24f741675b66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "scores",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True),
        sa.Column("amount", sa.Integer, default=0),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )



def downgrade() -> None:
    op.drop_table("scores")
