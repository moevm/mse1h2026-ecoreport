"""rename_file_id_to_file_name

Revision ID: 90509d2f6ead
Revises: f71775507d0f
Create Date: 2026-03-31 20:54:23.606365

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '90509d2f6ead'
down_revision: Union[str, Sequence[str], None] = 'f71775507d0f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('reports', 'file_id', new_column_name='file_name')


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('reports', 'file_name', new_column_name='file_id')
