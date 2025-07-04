"""Agregar campo discount a productos y state a tiendas

Revision ID: 7fdd694ef442
Revises: f5d853f64f65
Create Date: 2025-06-21 14:24:51.422499

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7fdd694ef442'
down_revision = 'f5d853f64f65'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('discount', sa.Float(), nullable=True))

    with op.batch_alter_table('shop', schema=None) as batch_op:
        op.execute("CREATE TYPE shop_state AS ENUM ('accepted', 'pending', 'declined')")
        batch_op.add_column(sa.Column('state', postgresql.ENUM('accepted', 'pending', 'declined', name='shop_state'), nullable=False, server_default='pending'))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shop', schema=None) as batch_op:
        batch_op.drop_column('state')

    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('discount')

    # ### end Alembic commands ###
