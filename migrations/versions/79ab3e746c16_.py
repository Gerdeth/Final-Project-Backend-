"""empty message

Revision ID: 79ab3e746c16
Revises: 69381017a676
Create Date: 2020-09-04 19:05:27.501359

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79ab3e746c16'
down_revision = '69381017a676'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transaction', sa.Column('value', sa.Float(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('transaction', 'value')
    # ### end Alembic commands ###