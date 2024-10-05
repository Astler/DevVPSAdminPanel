"""Add layers column to deleted_banner_model

Revision ID: d54d90a07fa3
Revises: 
Create Date: 2024-09-28 14:12:43.442187

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd54d90a07fa3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_table('deleted_banner_item')
    op.drop_table('admin_action_item')
    with op.batch_alter_table('deleted_banner_model', schema=None) as batch_op:
        batch_op.add_column(sa.Column('layers', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('deleted_banner_model', schema=None) as batch_op:
        batch_op.drop_column('layers')

    op.create_table('admin_action_item',
    sa.Column('record_id', sa.INTEGER(), nullable=False),
    sa.Column('admin_id', sa.VARCHAR(length=200), nullable=True),
    sa.Column('action_info', sa.VARCHAR(length=200), nullable=True),
    sa.Column('action', sa.INTEGER(), nullable=True),
    sa.Column('date', sa.BIGINT(), nullable=True),
    sa.PrimaryKeyConstraint('record_id')
    )
    op.create_table('deleted_banner_item',
    sa.Column('record_id', sa.INTEGER(), nullable=False),
    sa.Column('id', sa.VARCHAR(length=100), nullable=True),
    sa.Column('content', sa.VARCHAR(), nullable=True),
    sa.Column('date', sa.BIGINT(), nullable=True),
    sa.PrimaryKeyConstraint('record_id')
    )
    # ### end Alembic commands ###
