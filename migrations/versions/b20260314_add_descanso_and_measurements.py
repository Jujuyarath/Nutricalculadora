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
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Columnas para ejercicios
    existing_ejercicios = [c['name'] for c in inspector.get_columns('ejercicios')]
    if 'descanso' not in existing_ejercicios:
        op.add_column('ejercicios', sa.Column('descanso', sa.Integer(), server_default='60', nullable=True))
    
    # Columnas para historial
    existing_historial = [c['name'] for c in inspector.get_columns('historial')]
    cols_to_add = [
        ('peso', sa.Numeric()),
        ('altura', sa.Numeric()),
        ('cuello', sa.Numeric()),
        ('abdomen', sa.Numeric()),
        ('cintura', sa.Numeric()),
        ('cadera', sa.Numeric()),
        ('brazo', sa.Numeric()),
        ('pierna', sa.Numeric()),
    ]
    
    for col_name, col_type in cols_to_add:
        if col_name not in existing_historial:
            op.add_column('historial', sa.Column(col_name, col_type, nullable=True))


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Quitar de historial
    existing_historial = [c['name'] for c in inspector.get_columns('historial')]
    for col_name in ['pierna', 'brazo', 'cadera', 'cintura', 'abdomen', 'cuello', 'altura', 'peso']:
        if col_name in existing_historial:
            op.drop_column('historial', col_name)
            
    # Quitar de ejercicios
    existing_ejercicios = [c['name'] for c in inspector.get_columns('ejercicios')]
    if 'descanso' in existing_ejercicios:
        op.drop_column('ejercicios', 'descanso')
