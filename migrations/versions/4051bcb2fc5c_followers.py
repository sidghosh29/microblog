"""followers

Revision ID: 4051bcb2fc5c
Revises: 3c2bb0d7a05b
Create Date: 2025-03-29 12:10:27.676124

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4051bcb2fc5c'
down_revision = '3c2bb0d7a05b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=False),
    sa.Column('followed_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('follower_id', 'followed_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('followers')
    # ### end Alembic commands ###
