"""test migration.

Revision ID: b4f8c9e03ca7
Revises: 94924f882dc4
Create Date: 2020-05-13 07:18:59.795902

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b4f8c9e03ca7'
down_revision = '94924f882dc4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('job_id', sa.String(length=200), nullable=True))
    op.add_column('posts', sa.Column('link_post', sa.String(length=200), nullable=True))
    op.add_column('posts', sa.Column('notes', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'notes')
    op.drop_column('posts', 'link_post')
    op.drop_column('posts', 'job_id')
    # ### end Alembic commands ###
