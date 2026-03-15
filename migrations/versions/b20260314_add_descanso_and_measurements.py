"""add descanso and measurements

Revision ID: b20260314_add
Revises: afe7ded8b3a3
Create Date: 2026-03-14 18:50:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b20260314_add'
down_revision = 'afe7ded8b3a3'
branch_labels = None
depends_on = None


def upgrade():
    # Agregar descanso a ejercicios
    op.add_column('ejercicios', sa.Column('descanso', sa.Integer(), server_default='60', nullable=True))
    
    # Agregar columnas a historial
    op.add_column('historial', sa.Column('peso', sa.Numeric(), nullable=True))
    op.add_column('historial', sa.Column('altura', sa.Numeric(), nullable=True))
    op.add_column('historial', sa.Column('cuello', sa.Numeric(), nullable=True))
    op.add_column('historial', sa.Column('abdomen', sa.Numeric(), nullable=True))
    op.add_column('historial', sa.Column('cintura', sa.Numeric(), nullable=True))
    op.add_column('historial', sa.Column('cadera', sa.Numeric(), nullable=True))
    op.add_column('historial', sa.Column('brazo', sa.Numeric(), nullable=True))
    op.add_column('historial', sa.Column('pierna', sa.Numeric(), nullable=True))


def downgrade():
    op.drop_column('historial', 'pierna')
    op.drop_column('historial', 'brazo')
    op.drop_column('historial', 'cadera')
    op.drop_column('historial', 'cintura')
    op.drop_column('historial', 'abdomen')
    op.drop_column('historial', 'cuello')
    op.drop_column('historial', 'altura')
    op.drop_column('historial', 'peso')
    op.drop_column('ejercicios', 'descanso')
