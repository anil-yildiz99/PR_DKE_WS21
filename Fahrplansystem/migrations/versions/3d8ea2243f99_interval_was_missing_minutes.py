"""interval was missing minutes

Revision ID: 3d8ea2243f99
Revises: 430a81a09d9d
Create Date: 2021-12-24 10:47:09.586568

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d8ea2243f99'
down_revision = '430a81a09d9d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('interval', schema=None) as batch_op:
        batch_op.add_column(sa.Column('interval_minutes', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('interval', schema=None) as batch_op:
        batch_op.drop_column('interval_minutes')

    # ### end Alembic commands ###
