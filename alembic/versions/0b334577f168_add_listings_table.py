"""Add listings table

Revision ID: 0b334577f168
Revises: 55854d087a67
Create Date: 2020-07-18 17:33:13.463020

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b334577f168'
down_revision = '55854d087a67'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('listings',
    sa.Column('user_id', sa.BIGINT(), nullable=False),
    sa.Column('guild_id', sa.BIGINT(), nullable=True),
    sa.Column('invite_key', sa.Text(), nullable=True),
    sa.Column('open_time', sa.TIMESTAMP(), nullable=True),
    sa.Column('message', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['guild_id'], ['guilds.id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('listings')
    # ### end Alembic commands ###
