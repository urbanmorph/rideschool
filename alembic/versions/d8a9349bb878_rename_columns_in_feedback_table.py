"""rename columns in feedback table 

Revision ID: d8a9349bb878
Revises: 9ca7f0456e5c
Create Date: 2024-03-01 14:59:51.168120

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8a9349bb878'
down_revision: Union[str, None] = '9ca7f0456e5c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('feedback') as batch_op:
        # rename columns
        batch_op.alter_column('feedback_id', new_column_name='id')
        batch_op.alter_column('rate_training_sessions', new_column_name='sessions_rating')
        batch_op.alter_column('learner_guide_useful', new_column_name='lguide_useful')
        batch_op.alter_column('confident_to_ride', new_column_name='confident')
        batch_op.alter_column('trainer_evaluation', new_column_name='trainer_rating')
        batch_op.alter_column('feedback_status', new_column_name='status')

def downgrade() -> None:
    with op.batch_alter_table('feedback') as batch_op:
        # rename columns back to original names
        batch_op.alter_column('id', new_column_name='feedback_id')
        batch_op.alter_column('sessions_rating', new_column_name='rate_training_sessions')
        batch_op.alter_column('lguide_useful', new_column_name='learner_guide_useful')
        batch_op.alter_column('confident', new_column_name='confident_to_ride')
        batch_op.alter_column('trainer_rating', new_column_name='trainer_evaluation')
        batch_op.alter_column('status', new_column_name='feedback_status')
        
