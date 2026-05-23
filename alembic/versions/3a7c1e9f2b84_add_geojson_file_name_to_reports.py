"""add_geojson_file_name_to_reports

Revision ID: 3a7c1e9f2b84
Revises: 90509d2f6ead
Create Date: 2026-05-23 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a7c1e9f2b84'
down_revision: Union[str, Sequence[str], None] = '90509d2f6ead'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('reports', sa.Column('geojson_file_name', sa.String(255), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('reports', 'geojson_file_name')
