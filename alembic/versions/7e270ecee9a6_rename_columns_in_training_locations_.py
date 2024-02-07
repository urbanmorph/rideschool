"""Rename columns in training_locations_list table

Revision ID: 7e270ecee9a6
Revises: 
Create Date: 2024-02-01 10:21:25.931149

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e270ecee9a6'
#down_revision: Union[str, None] = '2fa2940339de'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename the columns
    op.alter_column('training_locations_list', 'training_location_id', new_column_name='id')
    op.alter_column('training_locations_list', 'training_location_address', new_column_name='address')
    op.alter_column('training_locations_list', 'training_location_latitude', new_column_name='latitude')
    op.alter_column('training_locations_list', 'training_location_longitude', new_column_name='longitude')
    op.alter_column('training_locations_list', 'training_location_created', new_column_name='created_date')
    op.alter_column('training_locations_list', 'training_location_updated', new_column_name='updated_date')
    op.alter_column('training_locations_list', 'training_location_picture', new_column_name='picture_path')

    # Rename primary key constraint
    op.drop_constraint('training_locations_list_pkey', 'training_locations_list', type_='primary')
    op.create_primary_key('training_locations_list_pkey', 'training_locations_list', ['id'])

    # Rename the trigger    
    op.execute('''
        CREATE OR REPLACE FUNCTION public.update_training_location_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_date := CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER update_training_location_updated_at
        BEFORE UPDATE 
        ON public.training_locations_list
        FOR EACH ROW
        EXECUTE FUNCTION public.update_training_location_updated_at();
    ''')



def downgrade() -> None:
     # Drops the trigger and the trigger function
    op.execute('DROP TRIGGER IF EXISTS update_training_location_updated_at ON public.training_locations_list')
    op.execute('DROP FUNCTION IF EXISTS public.update_training_location_updated_at CASCADE')
    # Rename columns back to their original names
    op.alter_column('training_locations_list', 'id', new_column_name='training_location_id')
    op.alter_column('training_locations_list', 'address', new_column_name='training_location_address')
    op.alter_column('training_locations_list', 'latitude', new_column_name='training_location_latitude')
    op.alter_column('training_locations_list', 'longitude', new_column_name='training_location_longitude')
    op.alter_column('training_locations_list', 'created_date', new_column_name='training_location_created')
    op.alter_column('training_locations_list', 'updated_date', new_column_name='training_location_updated')
    op.alter_column('training_locations_list', 'picture_path', new_column_name='training_location_picture')

    # Rename primary key constraint
    op.drop_constraint('training_locations_list_pkey', 'training_locations_list', type_='primary')
    op.create_primary_key('training_locations_list_pkey', 'training_locations_list', ['training_location_id'])
    #pass