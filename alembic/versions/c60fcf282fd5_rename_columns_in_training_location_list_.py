"""rename columns in training_location_list table

Revision ID: c60fcf282fd5
Revises: d0cde6562e31
Create Date: 2024-03-01 14:52:58.291292

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c60fcf282fd5'
down_revision: Union[str, None] = 'd0cde6562e31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('training_locations_list') as batch_op:
        # Rename the columns
        batch_op.alter_column('training_location_id', new_column_name='id')
        batch_op.alter_column('training_location_address', new_column_name='address')
        batch_op.alter_column('training_location_latitude', new_column_name='latitude')
        batch_op.alter_column('training_location_longitude', new_column_name='longitude')
        batch_op.alter_column('training_location_created', new_column_name='created_date')
        batch_op.alter_column('training_location_updated', new_column_name='updated_date')
        batch_op.alter_column('training_location_picture', new_column_name='picture_path')

        # Rename primary key constraint
        batch_op.drop_constraint('training_locations_list_pkey', type_='primary')
        batch_op.create_primary_key('training_locations_list_pkey', ['id'])

        # Drop existing trigger and triger function if it exists
        batch_op.execute('DROP TRIGGER IF EXISTS update_training_location_updated_at ON public.training_locations_list')
        batch_op.execute('DROP FUNCTION IF EXISTS public.update_training_location_updated_at CASCADE')

            
        # Rename the trigger
        batch_op.execute('''
            CREATE OR REPLACE FUNCTION public.update_training_location_updated()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_date := CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER update_training_location_updated
            BEFORE UPDATE 
            ON public.training_locations_list
            FOR EACH ROW
            EXECUTE FUNCTION public.update_training_location_updated();
        ''')


def downgrade() -> None:
     with op.batch_alter_table('training_locations_list') as batch_op:
        # Drop trigger and the trigger function
        batch_op.execute('DROP TRIGGER IF EXISTS update_training_location_updated ON public.training_locations_list')
        batch_op.execute('DROP FUNCTION IF EXISTS public.update_training_location_updated CASCADE')

        # Rename columns back to their original names
        batch_op.alter_column('id', new_column_name='training_location_id')
        batch_op.alter_column('address', new_column_name='training_location_address')
        batch_op.alter_column('latitude', new_column_name='training_location_latitude')
        batch_op.alter_column('longitude', new_column_name='training_location_longitude')
        batch_op.alter_column('created_date', new_column_name='training_location_created')
        batch_op.alter_column('updated_date', new_column_name='training_location_updated')
        batch_op.alter_column('picture_path', new_column_name='training_location_picture')

        # Recreate primary key constraint
        batch_op.drop_constraint('training_locations_list_pkey', type_='primary')
        batch_op.create_primary_key('training_locations_list_pkey', ['training_location_id'])

        # Recreate the trigger and the triger function to its original name 
        batch_op.execute('''
            CREATE OR REPLACE FUNCTION public.update_training_location_updated_at()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.training_location_updated := CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER update_training_location_updated_at
            BEFORE UPDATE 
            ON public.training_locations_list
            FOR EACH ROW
            EXECUTE FUNCTION public.update_training_location_updated_at();
        ''')
