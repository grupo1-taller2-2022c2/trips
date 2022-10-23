"""add_driver_location

Revision ID: d1e7454dbac2
Revises: a7099b114f6e
Create Date: 2022-10-23 02:38:38.398319

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1e7454dbac2'
down_revision = 'a7099b114f6e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('DriversLocation',
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('street_name', sa.String(), nullable=True),
    sa.Column('street_num', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('DriversLocation')
    # ### end Alembic commands ###
