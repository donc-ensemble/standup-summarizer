"""set_empty_strings_for_null_summaries

Revision ID: 412034bb04e8
Revises: 6635baf1a963
Create Date: 2025-04-07 21:44:09.912107

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '412034bb04e8'
down_revision: Union[str, None] = '6635baf1a963'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE summaries SET transcript = '' WHERE transcript IS NULL")
    op.execute("UPDATE summaries SET summary = '' WHERE summary IS NULL")
    
    # Alter columns to be non-nullable (optional)
    op.alter_column('summaries', 'transcript',
                  existing_type=sa.String(),
                  nullable=False)
    op.alter_column('summaries', 'summary',
                  existing_type=sa.String(),
                  nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('summaries', 'transcript',
                      existing_type=sa.String(),
                      nullable=True)
    op.alter_column('summaries', 'summary',
                  existing_type=sa.String(),
                  nullable=True)
