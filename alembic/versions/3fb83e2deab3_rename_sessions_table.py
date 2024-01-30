"""rename sessions table 

Revision ID: 3fb83e2deab3
Revises: 70eed478de13
Create Date: 2024-01-30 06:19:56.439183

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3fb83e2deab3'
down_revision: Union[str, None] = '70eed478de13'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
   ## op.alter_column('participants', 'participant_id', new_column_name='participant_id')
    #adding foreign key constraint
    ##op.create_foreign_key('fk_sessions_participant_id', 'sessions', 'participants', ['participant_id'], ['id'])
    ##op.alter_column('sessions', 'session_status', new_column_name='status')
    op.create_foreign_key(
        'fk_sessions_trainer_id',
        'sessions', 'trainer',
        ['trainer_id'], ['id'],
         ondelete='SET NULL'
        
    )
    op.create_foreign_key(
        'fk_sessions_participant_id',
        'sessions', 'participants',
        ['participant_id'], ['id'],
         ondelete='SET NULL'
        
    )


def downgrade() -> None:
    # Drop the foreign key constraint
    #op.drop_constraint('fk_sessions_participant_id', 'sessions', type_='foreignkey')

    # Rename the column back to its original name
    ##op.alter_column('sessions', 'participant_id', new_column_name='participant_id')
    
    #op.alter_column('sessions', 'status', new_column_name='session_status')
    
    op.drop_constraint('fk_sessions_trainer_id', 'sessions', type_='foreignkey')
    op.drop_constraint('fk_sessions_participant_id', 'sessions', type_='foreignkey')
