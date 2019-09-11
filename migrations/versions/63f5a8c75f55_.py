"""empty message

Revision ID: 63f5a8c75f55
Revises: 86e886177a63
Create Date: 2019-09-10 16:17:29.837713

"""

# revision identifiers, used by Alembic.
revision = '63f5a8c75f55'
down_revision = '86e886177a63'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('results',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('route', sa.String(length=80), nullable=False),
    sa.Column('dates', sa.String(length=100), nullable=False),
    sa.Column('result_all', postgresql.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sailings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('departure_time', sa.DateTime(), nullable=False),
    sa.Column('arrival_time', sa.DateTime(), nullable=False),
    sa.Column('departure_terminal', sa.String(), nullable=True),
    sa.Column('arrival_terminal', sa.String(), nullable=True),
    sa.Column('vessel_name', sa.String(), nullable=True),
    sa.Column('reservations_available', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sailings')
    op.drop_table('results')
    ### end Alembic commands ###
