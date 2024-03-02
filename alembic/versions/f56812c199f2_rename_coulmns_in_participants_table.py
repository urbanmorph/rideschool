"""rename coulmns in participants table 

Revision ID: f56812c199f2
Revises: e6e1561bf523
Create Date: 2024-03-01 14:58:17.621205

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f56812c199f2'
down_revision: Union[str, None] = 'e6e1561bf523'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
     with op.batch_alter_table('participants') as batch_op:
        # Rename columns
        batch_op.alter_column('participant_id', new_column_name='id')
        batch_op.alter_column('participant_name', new_column_name='name')
        batch_op.alter_column('participant_email', new_column_name='email')
        batch_op.alter_column('participant_contact', new_column_name='contact')
        batch_op.alter_column('participant_address', new_column_name='address')
        batch_op.alter_column('participant_age', new_column_name='age')
        batch_op.alter_column('participant_gender', new_column_name='gender')
        batch_op.alter_column('training_location_id', new_column_name='t_location_id')
        batch_op.alter_column('participant_created_at', new_column_name='created_date')
        batch_op.alter_column('participant_updated_at', new_column_name='updated_date')
        batch_op.alter_column('participant_status', new_column_name='status')
        batch_op.alter_column('participant_code', new_column_name='code')
        batch_op.alter_column('training_start_date', new_column_name='training_start')
        batch_op.alter_column('training_end_date', new_column_name='training_end')

        # drop and create newPrimary key constraint
        batch_op.drop_constraint('participants_pkey', type_='primary')
        batch_op.create_primary_key('participants_pkey', ['id'])

        # add Foreign key constraint
        batch_op.create_foreign_key(
            'fk_participants_t_location_id',
            'training_locations_list',
            ['t_location_id'],
            ['id']
        )

        # Drop existing trigger and trigger function if they exist
        batch_op.execute('DROP TRIGGER IF EXISTS update_participant_updated_at ON public.participants')
        batch_op.execute('DROP FUNCTION IF EXISTS public.update_participant_updated_at CASCADE')

        
        batch_op.execute('''
            CREATE OR REPLACE FUNCTION public.update_participant_updated_at()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_date := CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER update_participant_trigger
            BEFORE UPDATE 
            ON public.participants
            FOR EACH ROW
            EXECUTE FUNCTION public.update_participant_updated_at();
        ''')


def downgrade() -> None:
    with op.batch_alter_table('participants') as batch_op:
        # Revert trigger function change
        batch_op.execute('DROP TRIGGER IF EXISTS update_participant_trigger ON participants')
        batch_op.execute('DROP FUNCTION IF EXISTS public.update_participant_updated_at CASCADE')

        # Revert foreign key constraint
        batch_op.drop_constraint('fk_participants_t_location_id', type_='foreignkey')

        # Revert column name changes
        batch_op.alter_column('id', new_column_name='participant_id')
        batch_op.alter_column('name', new_column_name='participant_name')
        batch_op.alter_column('email', new_column_name='participant_email')
        batch_op.alter_column('contact', new_column_name='participant_contact')
        batch_op.alter_column('address', new_column_name='participant_address')
        batch_op.alter_column('age', new_column_name='participant_age')
        batch_op.alter_column('gender', new_column_name='participant_gender')
        batch_op.alter_column('t_location_id', new_column_name='training_location_id')
        batch_op.alter_column('created_date', new_column_name='participant_created_at')
        batch_op.alter_column('updated_date', new_column_name='participant_updated_at')
        batch_op.alter_column('status', new_column_name='participant_status')
        batch_op.alter_column('code', new_column_name='participant_code')
        batch_op.alter_column('training_start', new_column_name='training_start_date')
        batch_op.alter_column('training_end', new_column_name='training_end_date')
        # Revert primary key constraint
        batch_op.drop_constraint('participants_pkey', type_='primary')
        batch_op.create_primary_key('participants_pkey', ['participant_id'])


        # Recreate trigger with original name and definition
        batch_op.execute('''
            CREATE OR REPLACE FUNCTION public.update_participant_updated_at()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.participant_updated_at := CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER update_participant_updated_at
            BEFORE UPDATE 
            ON public.participants
            FOR EACH ROW
            EXECUTE FUNCTION public.update_participant_updated_at();
        ''')
