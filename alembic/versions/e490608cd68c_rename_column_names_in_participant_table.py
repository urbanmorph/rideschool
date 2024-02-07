""" rename column names in participant table 

Revision ID: e490608cd68c
Revises: bd49d8c051a2
Create Date: 2024-02-05 10:04:00.329857

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e490608cd68c'
down_revision: Union[str, None] = 'bd49d8c051a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    
    op.alter_column('participants', 'participant_id', new_column_name='id')
    op.alter_column('participants', 'participant_name', new_column_name='name')
    op.alter_column('participants', 'participant_email', new_column_name='email')
    op.alter_column('participants', 'participant_contact', new_column_name='contact')
    op.alter_column('participants', 'participant_address', new_column_name='address')
    op.alter_column('participants', 'participant_age', new_column_name='age')
    op.alter_column('participants', 'participant_gender', new_column_name='gender')
    op.alter_column('participants', 'training_location_id', new_column_name='t_location_id')
    op.alter_column('participants', 'participant_created_at', new_column_name='created_date')
    op.alter_column('participants', 'participant_updated_at', new_column_name='updated_date')
    op.alter_column('participants', 'participant_status', new_column_name='status')
    op.alter_column('participants', 'participant_code', new_column_name='code')
    op.alter_column('participants', 'training_start_date',new_column_name='training_start')
    op.alter_column('participants', 'training_end_date',new_column_name='training_end')

    # pk constraint
    op.drop_constraint('participants_pkey', 'participants', type_='primary')
    op.create_primary_key('participants_pkey', 'participants', ['id'])

    # adding foreign key constraint
    op.create_foreign_key('fk_participants_t_location_id', 'participants', 'training_locations_list', ['t_location_id'], ['id'])

    # Change trigger function 
    op.execute('DROP TRIGGER IF EXISTS update_participant_updated_at ON public.participants')
    op.execute('''
        CREATE OR REPLACE FUNCTION public.update_participant_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_date := CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER update_participant_updated_at
        BEFORE UPDATE 
        ON public.participants
        FOR EACH ROW
        EXECUTE FUNCTION public.update_participant_updated_at();
    ''')


def downgrade() -> None:
    op.drop_constraint('participants_pkey', 'participants', type_='primary')
    op.create_primary_key('participants_pkey', 'participants', ['id'])

    op.drop_constraint('fk_participants_t_location_id', 'participants', type_='foreignkey')
    op.create_foreign_key('fk_participants_t_location_id', 'participants', 'training_locations_list', ['t_location_id'], ['id'])
    
    op.alter_column('participants', 'participant_id', new_column_name='id')
    op.alter_column('participants', 'participant_name', new_column_name='name')
    op.alter_column('participants', 'participant_email', new_column_name='email')
    op.alter_column('participants', 'participant_contact', new_column_name='contact')
    op.alter_column('participants', 'participant_address', new_column_name='address')
    op.alter_column('participants', 'participant_age', new_column_name='age')
    op.alter_column('participants', 'participant_gender', new_column_name='gender')
    op.alter_column('participants', 'training_location_id', new_column_name='t_location_id')
    op.alter_column('participants', 'participant_created_at', new_column_name='created_date')
    op.alter_column('participants', 'participant_updated_at', new_column_name='updated_date')
    op.alter_column('participants', 'participant_status', new_column_name='status')
    op.alter_column('participants', 'participant_code', new_column_name='code')
    op.alter_column('participants', 'training_start_date', new_column_name='training_start')
    op.alter_column('participants', 'training_end_date', new_column_name='training_end')
