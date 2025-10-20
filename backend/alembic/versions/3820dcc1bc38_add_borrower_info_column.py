"""add_borrower_info_column

Revision ID: 3820dcc1bc38
Revises: e024131443c3
Create Date: 2025-10-14 16:47:48.308199

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3820dcc1bc38'
down_revision: Union[str, Sequence[str], None] = 'e024131443c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add borrower_info column to artifacts table
    op.add_column('artifacts', sa.Column('borrower_info', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove borrower_info column from artifacts table
    op.drop_column('artifacts', 'borrower_info')
