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
    with op.batch_alter_table('sessions') as batch_op:
        # rename columns
        batch_op.alter_column('scheduled_datetime', new_column_name='scheduled_date')
        batch_op.alter_column('actual_datetime', new_column_name='actual_date')
        batch_op.alter_column('session_current_date', new_column_name='created_date')
        batch_op.alter_column('session_update_date', new_column_name='update_date')
        batch_op.alter_column('session_status', new_column_name='status')

        # update trigger function name
        batch_op.execute("DROP TRIGGER IF EXISTS update_session_update_date ON public.sessions")
        batch_op.execute('''
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

        # add foreign key constraints
        batch_op.create_foreign_key('fk_sessions_trainer_id', 'trainer', ['trainer_id'], ['id'])
        batch_op.create_foreign_key('fk_sessions_participant_id', 'participants', ['participant_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table('sessions') as batch_op:
        # Drop foreign key constraints
        batch_op.drop_constraint('fk_sessions_trainer_id', type_='foreignkey')
        batch_op.drop_constraint('fk_sessions_participant_id', type_='foreignkey')

        # rename columns back to their original names
        batch_op.alter_column('created_date', new_column_name='session_current_date')
        batch_op.alter_column('update_date', new_column_name='session_update_date')
        batch_op.alter_column('status', new_column_name='session_status')
        batch_op.alter_column('scheduled_date', new_column_name='scheduled_datetime')
        batch_op.alter_column('actual_date', new_column_name='actual_datetime')

        # update trigger function name back to original triger 
        batch_op.execute("DROP TRIGGER IF EXISTS update_date ON public.sessions")
        batch_op.execute('''
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

