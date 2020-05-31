"""Adds profiles table

Revision ID: 7c06a4f88ab4
Revises: a7e2c9f1beb9
Create Date: 2020-05-31 01:13:36.348721

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7c06a4f88ab4'
down_revision = 'a7e2c9f1beb9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('profiles',
    sa.Column('user_id', sa.BIGINT(), nullable=False),
    sa.Column('friend_code', sa.Text(), nullable=True),
    sa.Column('island_name', sa.Text(), nullable=True),
    sa.Column('user_name', sa.Text(), nullable=True),
    sa.Column('fruit', sa.Text(), nullable=True),
    sa.Column('is_northern', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('profiles')
    # ### end Alembic commands ###
