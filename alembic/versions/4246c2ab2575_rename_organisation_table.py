"""Rename organisation table

Revision ID: 4246c2ab2575
Revises: 3fb83e2deab3
Create Date: 2024-01-30 11:32:06.124956

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4246c2ab2575'
down_revision: Union[str, None] = '3fb83e2deab3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('organisation', 'organisation_id', new_column_name='id')
    op.alter_column('organisation', 'organisation_name', new_column_name='name')
    op.alter_column('organisation', 'organisation_address', new_column_name='address')
    op.alter_column('organisation', 'organisation_contact', new_column_name='contact')
    op.alter_column('organisation', 'organisation_email', new_column_name='email')
    op.alter_column('organisation', 'organisation_type', new_column_name='type')
    op.alter_column('organisation', 'organisation_activities', new_column_name='activities')
    #pass

def downgrade() -> None:
    op.alter_column('organisation', 'id', new_column_name='organisation_id')
    op.alter_column('organisation', 'name', new_column_name='organisation_name')
    op.alter_column('organisation', 'address', new_column_name='organisation_address')
    op.alter_column('organisation', 'contact', new_column_name='organisation_contact')
    op.alter_column('organisation', 'email', new_column_name='organisation_email')
    op.alter_column('organisation', 'type', new_column_name='organisation_type')
    op.alter_column('organisation', 'activities', new_column_name='organisation_activities')
    #pass
