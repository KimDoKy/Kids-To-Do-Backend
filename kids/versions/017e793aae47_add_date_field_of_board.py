"""add date field of board

Revision ID: 017e793aae47
Revises:
Create Date: 2023-01-15 18:22:38.519829

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '017e793aae47'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('boards', sa.Column('created_at', sa.DateTime(datetime.now())))
    op.add_column('boards', sa.Column('updated_at', sa.DateTime(datetime.now())))


def downgrade() -> None:
    op.drop_column('boards', 'created_at')
    op.drop_column('boards', 'updated_at')
