"""rename column names in sessions table 

Revision ID: 6c00ac4a141a
Revises: e490608cd68c
Create Date: 2024-02-05 10:57:46.702187

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c00ac4a141a'
down_revision: Union[str, None] = 'e490608cd68c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename columns
    op.alter_column('sessions', 'scheduled_datetime', new_columnc_name='scheduled_date')
    op.alter_column('sessions', 'actual_datetime', new_column_name='actual_date')
    op.alter_column('sessions', 'session_current_date', new_column_name='created_date')
    op.alter_column('sessions', 'session_update_date', new_column_name='update_date')
    op.alter_column('sessions', 'session_status', new_column_name='status')

    # Update trigger function name
    op.execute("DROP TRIGGER IF EXISTS update_session_update_date ON public.sessions")
    op.execute('''
        CREATE OR REPLACE FUNCTION public.update_date()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.update_date := CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER update_date
        BEFORE UPDATE 
        ON public.sessions
        FOR EACH ROW
        EXECUTE FUNCTION public.update_date();
    ''')

    # Add foreign key constraints
    op.create_foreign_key('fk_sessions_trainer_id', 'sessions', 'trainer', ['trainer_id'], ['id'])
    op.create_foreign_key('fk_sessions_participant_id', 'sessions', 'participants', ['participant_id'], ['participant_id'])



def downgrade() -> None:
    # Drop foreign key constraints
    op.drop_constraint('fk_sessions_trainer_id', 'sessions', type_='foreignkey')
    op.drop_constraint('fk_sessions_participant_id', 'sessions', type_='foreignkey')

    # Rename columns its to original names
    op.alter_column('sessions', 'created_date', new_column_name='session_current_date')
    op.alter_column('sessions', 'update_date', new_column_name='session_update_date')
    op.alter_column('sessions', 'status', new_column_name='session_status')
    op.alter_column('sessions', 'scheduled_date',new_columnc_name='scheduled_datetime')
    op.alter_column('sessions', 'actual_date', new_column_name='actual_datetime')

    # Update trigger function name back to original
    op.execute("DROP TRIGGER IF EXISTS update_date ON public.sessions")
    op.execute('''
        CREATE OR REPLACE FUNCTION public.update_session_update_date()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.session_update_date := CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER update_session_update_date
        BEFORE UPDATE 
        ON public.sessions
        FOR EACH ROW
        EXECUTE FUNCTION public.update_session_update_date();
    ''')
