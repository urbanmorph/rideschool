"""rename columns in organisation table 

Revision ID: be9b6f2295c9
Revises: c60fcf282fd5
Create Date: 2024-03-01 14:53:59.093606

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'be9b6f2295c9'
down_revision: Union[str, None] = 'c60fcf282fd5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('organisation') as batch_op:
        # Rename columns
        batch_op.alter_column('organisation_id', new_column_name='id')
        batch_op.alter_column('organisation_name', new_column_name='name')
        batch_op.alter_column('organisation_address', new_column_name='address')
        batch_op.alter_column('organisation_contact', new_column_name='contact')
        batch_op.alter_column('organisation_email', new_column_name='email')
        batch_op.alter_column('organisation_type', new_column_name='org_type')
        batch_op.alter_column('organisation_activities', new_column_name='activities')
        batch_op.alter_column('organisation_legal_status_document', new_column_name='legal_document')
        batch_op.alter_column('organisation_created_at', new_column_name='created_date')
        batch_op.alter_column('organisation_updated_at', new_column_name='updated_date')

        # Change primary key to new column name 
        batch_op.drop_constraint('organisation_pkey', type_='primary')
        batch_op.create_primary_key('organisation_pkey', ['id'])

        # Drop trigger and the trigger function
        batch_op.execute('DROP TRIGGER IF EXISTS update_organisation_trigger ON public.organisation')
        batch_op.execute('DROP FUNCTION IF EXISTS public.update_organisation_updated_at CASCADE')


        # Modify trigger function
        batch_op.execute('''
            CREATE OR REPLACE FUNCTION public.update_organisation_updated_at()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_date := CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER update_organisation_trigger
            BEFORE UPDATE 
            ON public.organisation
            FOR EACH ROW
            EXECUTE FUNCTION public.update_organisation_updated_at();
        ''')


def downgrade() -> None:
    with op.batch_alter_table('organisation') as batch_op:
        # Drop trigger and the trigger function
        batch_op.execute('DROP TRIGGER IF EXISTS update_organisation_trigger ON public.organisation')
        batch_op.execute('DROP FUNCTION IF EXISTS public.update_organisation_updated_at CASCADE')

        # Rename columns back to its original names
        batch_op.alter_column('id', new_column_name='organisation_id')
        batch_op.alter_column('name', new_column_name='organisation_name')
        batch_op.alter_column('address', new_column_name='organisation_address')
        batch_op.alter_column('contact', new_column_name='organisation_contact')
        batch_op.alter_column('email', new_column_name='organisation_email')
        batch_op.alter_column('org_type', new_column_name='organisation_type')
        batch_op.alter_column('activities', new_column_name='organisation_activities')
        batch_op.alter_column('legal_document', new_column_name='organisation_legal_status_document')
        batch_op.alter_column('created_date', new_column_name='organisation_created_at')
        batch_op.alter_column('updated_date', new_column_name='organisation_updated_at')
        
        # Change primary key back to the original column name 'organisation_id'
        batch_op.drop_constraint('organisation_pkey', type_='primary')
        batch_op.create_primary_key('organisation_pkey', ['organisation_id'])

        # Recreate the trigger and the function with the original name 
        batch_op.execute('''
            CREATE OR REPLACE FUNCTION public.update_organisation_updated_at()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.organisation_updated_at := CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER update_organisation_trigger
            BEFORE UPDATE 
            ON public.organisation
            FOR EACH ROW
            EXECUTE FUNCTION public.update_organisation_updated_at();
        ''')
