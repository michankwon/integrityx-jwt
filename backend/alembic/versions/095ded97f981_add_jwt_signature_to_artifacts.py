"""add jwt signature to artifacts

Revision ID: 095ded97f981
Revises: 3820dcc1bc38
Create Date: 2025-10-22 20:55:23.859279

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '095ded97f981'
down_revision: Union[str, Sequence[str], None] = '3820dcc1bc38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("artifacts", sa.Column("signature_jwt", sa.Text(), nullable=True))



def downgrade() -> None:
    op.drop_column("artifacts", "signature_jwt")
