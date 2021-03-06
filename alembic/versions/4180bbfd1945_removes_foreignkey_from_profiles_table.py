"""Removes ForeignKey from profiles table

Revision ID: 4180bbfd1945
Revises: 7c06a4f88ab4
Create Date: 2020-05-31 01:15:25.865222

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4180bbfd1945'
down_revision = '7c06a4f88ab4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('profiles_user_id_fkey', 'profiles', type_='foreignkey')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('profiles_user_id_fkey', 'profiles', 'users', ['user_id'], ['user_id'])
    # ### end Alembic commands ###
