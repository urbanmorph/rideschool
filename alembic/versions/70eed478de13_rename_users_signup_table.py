"""Rename users_signup table

Revision ID: 70eed478de13
Revises: a5adc765449c
Create Date: 2024-01-29 23:06:08.297642

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '70eed478de13'
down_revision: Union[str, None] = 'a5adc765449c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('users_signup', 'user_id', new_column_name='id')


def downgrade() -> None:
    op.alter_column('users_signup', 'id', new_column_name='user_id')
