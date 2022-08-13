"""empty message

Revision ID: 015ee44d49a8
Revises: 9d4d4ed78aed
Create Date: 2022-08-12 21:05:24.114982

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '015ee44d49a8'
down_revision = '9d4d4ed78aed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('website_link', sa.String(), nullable=True))
    op.add_column('Artist', sa.Column('seeking_talent', sa.String(), nullable=True))
    op.add_column('Artist', sa.Column('seeking_description', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'seeking_description')
    op.drop_column('Artist', 'seeking_talent')
    op.drop_column('Artist', 'website_link')
    # ### end Alembic commands ###
