"""add is_draft to reports

Revision ID: a1b2c3d4e5f6
Revises: ed2ca4b8b10b
Create Date: 2026-05-25 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '3ddc8d2fd17d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('reports', sa.Column('is_draft', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.alter_column('reports', 'is_draft', server_default=None)


def downgrade() -> None:
    op.drop_column('reports', 'is_draft')
