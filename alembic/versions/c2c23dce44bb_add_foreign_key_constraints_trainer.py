"""Add foreign key constraints trainer

Revision ID: c2c23dce44bb
Revises: 4246c2ab2575
Create Date: 2024-01-30 15:44:28.908588

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2c23dce44bb'
down_revision: Union[str, None] = '4246c2ab2575'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add foreign key constraint for training_location_id    
    op.create_foreign_key(
        'fk_training_location',
        'trainer', 'training_locations_list',
        ['training_location_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_trainer_organisation_id',
        'trainer',
        'organisation',
        ['organisation_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    # Drop foreign key constraint for training_location_id
    op.drop_constraint('fk_training_location', 'trainer', type_='foreignkey')

    # Drop foreign key constraint for organisation_id
    op.drop_constraint('fk_trainer_organisation_id', 'trainer', type_='foreignkey')
