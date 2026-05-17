from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '55018beab2be'
down_revision: Union[str, Sequence[str], None] = '90509d2f6ead'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('documents_gost',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('gost_r_72274_2025', sa.Boolean(), nullable=True),
        sa.Column('gost_1811_2019', sa.Boolean(), nullable=True),
        sa.Column('gost_4_225_83', sa.Boolean(), nullable=True),
        sa.Column('sp_32_13330_2018', sa.Boolean(), nullable=True),
        sa.Column('snip_32_03_96', sa.Boolean(), nullable=True),
        sa.Column('gost_r_71831_2024', sa.Boolean(), nullable=True),
        sa.Column('gost_r_54560_2015', sa.Boolean(), nullable=True),
        sa.Column('gost_286_82', sa.Boolean(), nullable=True),
        sa.Column('sp_100_13330_2016', sa.Boolean(), nullable=True),
        sa.Column('snip_2_06_15_85', sa.Boolean(), nullable=True),
        sa.Column('gost_r_71856_2024', sa.Boolean(), nullable=True),
        sa.Column('gost_33068_2014', sa.Boolean(), nullable=True),
        sa.Column('sanpin_2_1_3684_21', sa.Boolean(), nullable=True),
        sa.Column('sp_104_13330_2016', sa.Boolean(), nullable=True),
        sa.Column('snip_2_04_03_85', sa.Boolean(), nullable=True),
        sa.Column('gost_r_70628_1_2023', sa.Boolean(), nullable=True),
        sa.Column('gost_31416_2009', sa.Boolean(), nullable=True),
        sa.Column('sp_31_13330_2021', sa.Boolean(), nullable=True),
        sa.Column('sp_250_1325800_2016', sa.Boolean(), nullable=True),
        sa.Column('snip_2_05_02_85', sa.Boolean(), nullable=True),
        sa.Column('gost_r_70628_2_2023', sa.Boolean(), nullable=True),
        sa.Column('gost_6942_98', sa.Boolean(), nullable=True),
        sa.Column('sp_34_13330_2021', sa.Boolean(), nullable=True),
        sa.Column('sp_116_13330_2012', sa.Boolean(), nullable=True),
        sa.Column('snip_2_06_03_85', sa.Boolean(), nullable=True),
        sa.Column('gost_r_70628_5_2023', sa.Boolean(), nullable=True),
        sa.Column('gost_17_1_3_13_86', sa.Boolean(), nullable=True),
        sa.Column('sp_121_13330_2019', sa.Boolean(), nullable=True),
        sa.Column('sp_50_101_2004', sa.Boolean(), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('test_results',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('results_ph', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('results_iron', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('results_manganese', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('results_nitrates', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('results_sulfates', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_name', sa.String(length=100), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('image_path', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.Date(), nullable=True),
        sa.Column('update_at', sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('file',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('full_object_name', sa.String(length=500), nullable=True),
        sa.Column('short_object_name', sa.String(length=500), nullable=True),
        sa.Column('organization_name', sa.String(length=500), nullable=True),
        sa.Column('region', sa.String(length=500), nullable=True),
        sa.Column('year', sa.Date(), nullable=True),
        sa.Column('gost_id', sa.Integer(), nullable=True),
        sa.Column('relief_type', sa.String(length=500), nullable=True),
        sa.Column('soil_type', sa.String(length=500), nullable=True),
        sa.Column('groundwater_level', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('climate_zone', sa.String(length=500), nullable=True),
        sa.Column('coordinates_latitude', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('coordinates_longitude', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('object_type', sa.String(length=500), nullable=True),
        sa.Column('system_type', sa.String(length=500), nullable=True),
        sa.Column('pipe_material', sa.String(length=500), nullable=True),
        sa.Column('pipe_diameter', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('pipe_depth', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('pipe_length', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('pipe_install_year', sa.Date(), nullable=True),
        sa.Column('manhole_count', sa.Integer(), nullable=True),
        sa.Column('monitoring_point_count', sa.Integer(), nullable=True),
        sa.Column('observation_frequency', sa.String(length=500), nullable=True),
        sa.Column('test_results_id', sa.Integer(), nullable=True),
        sa.Column('organization_address', sa.String(length=500), nullable=True),
        sa.Column('organization_phone', sa.String(length=500), nullable=True),
        sa.Column('organization_email', sa.String(length=500), nullable=True),
        sa.Column('responsible_name', sa.String(length=500), nullable=True),
        sa.Column('responsible_position', sa.String(length=500), nullable=True),
        sa.Column('report_date', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['gost_id'], ['documents_gost.id'], ),
        sa.ForeignKeyConstraint(['test_results_id'], ['test_results.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('observation_dinamic',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('file_id', sa.Integer(), nullable=True),
        sa.Column('dinamic_ph', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('dinamic_iron', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('dinamic_manganese', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('dinamic_nitrates', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('dinamic_sulfates', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('dinamic_data', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['file_id'], ['file.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('observation_point',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('file_id', sa.Integer(), nullable=True),
        sa.Column('observation_point', sa.String(length=500), nullable=True),
        sa.Column('latitude', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('longitude', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('medium_type', sa.String(length=500), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['file_id'], ['file.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.add_column('reports', sa.Column('file_id', sa.Integer(), nullable=False))
    op.alter_column('reports', 'user_id',
                existing_type=sa.VARCHAR(length=255),
                type_=sa.Integer(),
                existing_nullable=False,
                postgresql_using="user_id::integer")
    op.create_foreign_key(None, 'reports', 'file', ['file_id'], ['id'])
    op.create_foreign_key(None, 'reports', 'user', ['user_id'], ['id'])
    op.drop_column('reports', 'file_name')

def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('reports', sa.Column('file_name', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'reports', type_='foreignkey')
    op.drop_constraint(None, 'reports', type_='foreignkey')
    op.alter_column('reports', 'user_id',
            existing_type=sa.Integer(),
            type_=sa.VARCHAR(length=255),
            existing_nullable=False,
            postgresql_using="user_id::varchar")
    op.drop_column('reports', 'file_id')
    op.drop_table('observation_point')
    op.drop_table('observation_dinamic')
    op.drop_table('file')
    op.drop_table('user')
    op.drop_table('test_results')
    op.drop_table('documents_gost')