"""existing

Revision ID: 6ad489baad27
Revises: 
Create Date: 2024-03-01 12:10:44.403277

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ad489baad27'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # op.execute is an alembic method to call sql
    with open('existing-database.sql') as file:
        op.execute(file.read())


def downgrade() -> None:
    pass
