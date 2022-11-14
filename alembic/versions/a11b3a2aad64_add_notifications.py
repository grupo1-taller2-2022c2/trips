"""add notifications

Revision ID: a11b3a2aad64
Revises: e6d932752867
Create Date: 2022-10-30 18:17:08.758936

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a11b3a2aad64'
down_revision = 'e6d932752867'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('NotificationToken',
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('token', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('NotificationToken')
    # ### end Alembic commands ###