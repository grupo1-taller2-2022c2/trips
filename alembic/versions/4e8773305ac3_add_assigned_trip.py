"""add_assigned_trip

Revision ID: 4e8773305ac3
Revises: e6d932752867
Create Date: 2022-11-12 17:55:46.191828

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e8773305ac3'
down_revision = 'e6d932752867'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('DriversAssignedTrip',
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('trip_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('DriversAssignedTrip')
    # ### end Alembic commands ###