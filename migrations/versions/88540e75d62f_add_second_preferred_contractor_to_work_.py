"""Add second preferred contractor to work order

Revision ID: 88540e75d62f
Revises: ef61a3b6f232
Create Date: 2025-05-25 13:08:59.466678

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88540e75d62f'
down_revision = 'ef61a3b6f232'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('work_order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('second_preferred_contractor_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_work_order_second_preferred_contractor_id',
            'user',
            ['second_preferred_contractor_id'],
            ['id']
        )

def downgrade():
    with op.batch_alter_table('work_order', schema=None) as batch_op:
        batch_op.drop_constraint('fk_work_order_second_preferred_contractor_id', type_='foreignkey')
        batch_op.drop_column('second_preferred_contractor_id')

