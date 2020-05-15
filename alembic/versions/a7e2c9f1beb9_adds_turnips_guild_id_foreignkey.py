"""adds turnips guild_id foreignkey

Revision ID: a7e2c9f1beb9
Revises: 213503d71cdb
Create Date: 2020-05-14 22:44:20.924470

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a7e2c9f1beb9"
down_revision = "213503d71cdb"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("guilds", sa.Column("local_turnips", sa.Boolean(), nullable=True))
    op.create_foreign_key(None, "turnips", "guilds", ["guild_id"], ["id"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "turnips", type_="foreignkey")
    op.drop_column("guilds", "local_turnips")
    # ### end Alembic commands ###
