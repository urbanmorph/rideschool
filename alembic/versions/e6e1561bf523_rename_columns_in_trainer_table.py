"""rename columns in trainer table

Revision ID: e6e1561bf523
Revises: be9b6f2295c9
Create Date: 2024-03-01 14:55:04.365477

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6e1561bf523'
down_revision: Union[str, None] = 'be9b6f2295c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('trainer') as batch_op:
        # Rename columns
        batch_op.alter_column('trainer_id', new_column_name='id')
        batch_op.alter_column('trainer_name', new_column_name='name')
        batch_op.alter_column('trainer_email', new_column_name='email')
        batch_op.alter_column('trainer_contact', new_column_name='contact')
        batch_op.alter_column('trainer_address', new_column_name='address')
        batch_op.alter_column('trainer_age', new_column_name='age')
        batch_op.alter_column('trainer_gender', new_column_name='gender')
        batch_op.alter_column('trainer_education', new_column_name='education')
        batch_op.alter_column('trainer_aadhar_no', new_column_name='aadhar_no')
        batch_op.alter_column('trainer_created_at', new_column_name='created_date')
        batch_op.alter_column('trainer_updated_at', new_column_name='updated_date')
        batch_op.alter_column('trainer_training_completion_date', new_column_name='training_completion')
        batch_op.alter_column('training_location_id', new_column_name='t_location_id')
        batch_op.alter_column('organisation_id', new_column_name='org_id')
        batch_op.alter_column('trainer_language', new_column_name='language')
        batch_op.alter_column('trainer_status', new_column_name='status')
        batch_op.alter_column('trainer_code', new_column_name='code')

        # Adding foreign key constraints
        batch_op.create_foreign_key(
            'fk_trainer_t_location_id',
            'training_locations_list',
            ['t_location_id'],
            ['id']
        )

        batch_op.create_foreign_key(
            'fk_trainer_org_id',
            'organisation',
            ['org_id'],
            ['id']
        )

        # Rename primary key constraint
        batch_op.drop_constraint('trainer_pkey', type_='primary')
        batch_op.create_primary_key('trainer_pkey', ['id'])

        # Drop trigger and the trigger function if they exist
        batch_op.execute('DROP TRIGGER IF EXISTS trainer_updated_at_trigger ON public.trainer')
        batch_op.execute('DROP FUNCTION IF EXISTS public.update_trainer_updated_at CASCADE')

        # Recreate the trigger with the original name and definition
        batch_op.execute('''
            CREATE OR REPLACE FUNCTION public.update_trainer_updated_at()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_date := CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER trainer_updated_trigger
            BEFORE UPDATE 
            ON public.trainer
            FOR EACH ROW
            EXECUTE FUNCTION public.update_trainer_updated_at();
        ''')



def downgrade() -> None:
    with op.batch_alter_table('trainer') as batch_op:
        # Drop trigger and the trigger function
        batch_op.execute('DROP TRIGGER IF EXISTS trainer_updated_trigger ON public.trainer')
        batch_op.execute('DROP FUNCTION IF EXISTS public.update_trainer_updated_at CASCADE')

        # Recreate the trigger and trigger function with the original name 
        batch_op.execute('''
            CREATE OR REPLACE FUNCTION public.update_trainer_updated_at()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.trainer_updated_at := CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER trainer_updated_at_trigger
            BEFORE UPDATE 
            ON public.trainer
            FOR EACH ROW
            EXECUTE FUNCTION public.update_trainer_updated_at();
        ''')

        # Drop foreign key constraints
        batch_op.drop_constraint('fk_trainer_t_location_id', type_='foreignkey')
        batch_op.drop_constraint('fk_trainer_org_id', type_='foreignkey')

        # Rename columns back to the original names
        batch_op.alter_column('id', new_column_name='trainer_id')
        batch_op.alter_column('name', new_column_name='trainer_name')
        batch_op.alter_column('email', new_column_name='trainer_email')
        batch_op.alter_column('contact', new_column_name='trainer_contact')
        batch_op.alter_column('address', new_column_name='trainer_address')
        batch_op.alter_column('age', new_column_name='trainer_age')
        batch_op.alter_column('gender', new_column_name='trainer_gender')
        batch_op.alter_column('education', new_column_name='trainer_education')
        batch_op.alter_column('aadhar_no', new_column_name='trainer_aadhar_no')
        batch_op.alter_column('created_date', new_column_name='trainer_created_at')
        batch_op.alter_column('updated_date', new_column_name='trainer_updated_at')
        batch_op.alter_column('training_completion', new_column_name='trainer_training_completion_date')
        batch_op.alter_column('t_location_id', new_column_name='training_location_id')
        batch_op.alter_column('org_id', new_column_name='organisation_id')
        batch_op.alter_column('language', new_column_name='trainer_language')
        batch_op.alter_column('status', new_column_name='trainer_status')
        batch_op.alter_column('code', new_column_name='trainer_code')

        # Rename original primary key constraint
        batch_op.drop_constraint('trainer_pkey', type_='primary')
        batch_op.create_primary_key('trainer_pkey', ['trainer_id'])

