"""rename column names in trainer table

Revision ID: bd49d8c051a2
Revises: 5b3d07359781
Create Date: 2024-02-02 18:03:21.153313

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd49d8c051a2'
down_revision: Union[str, None] = '5b3d07359781'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename columns
    op.alter_column('trainer', 'trainer_id', new_column_name='id')
    op.alter_column('trainer', 'trainer_name', new_column_name='name')
    op.alter_column('trainer', 'trainer_email', new_column_name='email')
    op.alter_column('trainer', 'trainer_contact', new_column_name='contact')
    op.alter_column('trainer', 'trainer_address', new_column_name='address')
    op.alter_column('trainer', 'trainer_age', new_column_name='age')
    op.alter_column('trainer', 'trainer_gender', new_column_name='gender')
    op.alter_column('trainer', 'trainer_education', new_column_name='education')
    op.alter_column('trainer', 'trainer_aadhar_no', new_column_name='aadhar_no')
    op.alter_column('trainer', 'trainer_created_at', new_column_name='created_date')
    op.alter_column('trainer', 'trainer_updated_at', new_column_name='updated_date')
    op.alter_column('trainer', 'trainer_training_completion_date', new_column_name='training_completion')
    op.alter_column('trainer', 'training_location_id', new_column_name='t_location_id')
    op.alter_column('trainer', 'organisation_id', new_column_name='org_id')
    op.alter_column('trainer', 'trainer_language', new_column_name='language')
    op.alter_column('trainer', 'trainer_status', new_column_name='status')
    op.alter_column('trainer', 'trainer_code', new_column_name='code')
    # Adding  the foreign key constraint to ttl_id
    op.create_foreign_key(
        'fk_trainer_t_location_id',
        'trainer',
        'training_locations_list',
        ['t_location_id'],
        ['id']
    )

    # adding foreign key constraint to organisation_id
    op.create_foreign_key(
        'fk_trainer_org_id',
        'trainer',
        'organisation',
        ['org_id'],
        ['id']
    )
    # Rename primary key constraint
    op.drop_constraint('trainer_pkey', 'trainer', type_='primary')
    op.create_primary_key('trainer_pkey', 'trainer', ['id'])

    # Renames the trigger function
    op.execute('DROP TRIGGER IF EXISTS trainer_updated_at_trigger ON public.trainer')
    op.execute('''
        CREATE OR REPLACE FUNCTION public.update_trainer_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_date := CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trainer_updated_at_trigger
        BEFORE UPDATE 
        ON public.trainer
        FOR EACH ROW
        EXECUTE FUNCTION public.update_trainer_updated_at();
    ''')


def downgrade() -> None:
    # Drop trigger and the trigger function
    op.execute('DROP TRIGGER IF EXISTS trainer_updated_at_trigger ON public.trainer')
    op.execute('DROP FUNCTION IF EXISTS public.update_trainer_updated_at CASCADE')

    # Drop foreign key constraint
    op.drop_constraint('fk_trainer_t_location_id', 'trainer', type_='foreignkey')
    op.drop_constraint('fk_trainer_org_id', 'trainer', type_='foreignkey')

    # Rename columns back to the original names
    op.alter_column('trainer', 'id', new_column_name='trainer_id')
    op.alter_column('trainer', 'name', new_column_name='trainer_name')
    op.alter_column('trainer', 'email', new_column_name='trainer_email')
    op.alter_column('trainer', 'contact', new_column_name='trainer_contact')
    op.alter_column('trainer', 'address', new_column_name='trainer_address')
    op.alter_column('trainer', 'age', new_column_name='trainer_age')
    op.alter_column('trainer', 'gender', new_column_name='trainer_gender')
    op.alter_column('trainer', 'education', new_column_name='trainer_education')
    op.alter_column('trainer', 'aadhar_no', new_column_name='trainer_aadhar_no')
    op.alter_column('trainer', 'created_date', new_column_name='trainer_created_at')
    op.alter_column('trainer', 'updated_date', new_column_name='trainer_updated_at')
    op.alter_column('trainer', 'training_completion', new_column_name='trainer_training_completion_date')
    op.alter_column('trainer', 'org_id', new_column_name='organisation_id')
    op.alter_column('trainer', 't_location_id', new_column_name='training_location_id')
    op.alter_column('trainer', 'language', new_column_name='trainer_language')
    op.alter_column('trainer', 'status', new_column_name='trainer_status')
    op.alter_column('trainer', 'code', new_column_name='trainer_code')

    # Rename original primary key constraint
    op.drop_constraint('trainer_pkey', 'trainer', type_='primary')
    op.create_primary_key('trainer_pkey', 'trainer', ['trainer_id'])
