"""Initial migration

Revision ID: 82a72565d3be
Revises: d54d90a07fa3
Create Date: 2024-10-05 13:51:27.705216

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '82a72565d3be'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('action_item')
    with op.batch_alter_table('daily_banner_item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('layers', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('daily_banner_item', schema=None) as batch_op:
        batch_op.drop_column('layers')

    op.create_table('action_item',
    sa.Column('record_id', sa.INTEGER(), nullable=False),
    sa.Column('admin', sa.VARCHAR(length=200), nullable=True),
    sa.Column('action_data', sa.VARCHAR(length=200), nullable=True),
    sa.Column('action', sa.INTEGER(), nullable=True),
    sa.Column('date', sa.BIGINT(), nullable=True),
    sa.PrimaryKeyConstraint('record_id')
    )
    # ### end Alembic commands ###
