"""rename column names in organisation table

Revision ID: 5b3d07359781
Revises: 7e270ecee9a6
Create Date: 2024-02-02 17:57:50.376379

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b3d07359781'
down_revision: Union[str, None] = '7e270ecee9a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename columns
    op.alter_column('organisation', 'organisation_id', new_column_name='id')
    op.alter_column('organisation', 'organisation_name', new_column_name='name')
    op.alter_column('organisation', 'organisation_address', new_column_name='address')
    op.alter_column('organisation', 'organisation_contact', new_column_name='contact')
    op.alter_column('organisation', 'organisation_email', new_column_name='email')
    op.alter_column('organisation', 'organisation_type', new_column_name='org_type')
    op.alter_column('organisation', 'organisation_activities', new_column_name='activities')
    op.alter_column('organisation', 'organisation_legal_status_document', new_column_name='legal_document')
    
    op.alter_column('organisation', 'organisation_created_at', new_column_name='created_date')
    op.alter_column('organisation', 'organisation_updated_at', new_column_name='updated_date')
    

    # Change primary key to new column name 'id'
    op.drop_constraint('organisation_pkey', 'organisation', type_='primary')
    op.create_primary_key('organisation_pkey', 'organisation', ['id'])

    # Modify trigger function
    op.execute('DROP TRIGGER IF EXISTS update_organisation_trigger ON public.organisation')
    op.execute('''
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
    # Drop trigger and the trigger function
    op.execute('DROP TRIGGER IF EXISTS update_organisation_trigger ON public.organisation')
    op.execute('DROP FUNCTION IF EXISTS public.update_organisation_updated_at CASCADE')

    # Change primary key back to the original column name 'organisation_id'
    op.drop_constraint('organisation_pkey', 'organisation', type_='primary')
    op.create_primary_key('organisation_pkey', 'organisation', ['organisation_id'])

    # Rename columns back to its original names
    op.alter_column('organisation', 'id', new_column_name='organisation_id')
    op.alter_column('organisation', 'name', new_column_name='organisation_name')
    op.alter_column('organisation', 'address', new_column_name='organisation_address')
    op.alter_column('organisation', 'contact', new_column_name='organisation_contact')
    op.alter_column('organisation', 'email', new_column_name='organisation_email')
    op.alter_column('organisation', 'org_type', new_column_name='organisation_type')
    op.alter_column('organisation', 'activities', new_column_name='organisation_activities')
    op.alter_column('organisation', 'legal_document', new_column_name='organisation_legal_status_document')
    op.alter_column('organisation', 'created_date', new_column_name='organisation_created_at')
    op.alter_column('organisation', 'updated_date', new_column_name='organisation_updated_at')
    
