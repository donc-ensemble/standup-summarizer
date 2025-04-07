"""Add status column to summaries

Revision ID: 86bf65316808
Revises: 1d6e6169d686
Create Date: 2025-04-07 04:47:06.169891

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '86bf65316808'
down_revision: Union[str, None] = '1d6e6169d686'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.add_column('summaries', sa.Column('status', sa.String(), server_default='pending', nullable=True))

def downgrade():
    op.drop_column('summaries', 'status')