"""Rename training_locations_list table

Revision ID: 9d5e71c04a7f
Revises: e5e89371f078
Create Date: 2024-01-29 19:40:35.976310

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d5e71c04a7f'
down_revision: Union[str, None] = 'e5e89371f078'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# alembic upgrade head
def upgrade() -> None:
    #op.alter_column('training_locations_list', 'training_location_id', new_column_name='id')
    #op.alter_column('training_locations_list', 'training_location_address', new_column_name='address')
    #op.alter_column('training_locations_list', 'training_location_latitude', new_column_name='latitude')
    #op.alter_column('training_locations_list', 'training_location_longitude', new_column_name='longitude')
   pass

# to rollback the changes "alembic downgrade base"
def downgrade() -> None:
    op.alter_column('training_locations_list', 'id', new_column_name='training_location_id')
    op.alter_column('training_locations_list', 'address', new_column_name='training_location_address')
    op.alter_column('training_locations_list', 'latitude', new_column_name='training_location_latitude')
    op.alter_column('training_locations_list', 'longitude', new_column_name='training_location_longitude')
  