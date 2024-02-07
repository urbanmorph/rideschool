""" rename column names in feedback table 

Revision ID: d3a7180bed21
Revises: 6c00ac4a141a
Create Date: 2024-02-05 13:02:45.380164

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3a7180bed21'
down_revision: Union[str, None] = '6c00ac4a141a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('feedback', 'feedback_id', new_column_name='id')
    op.alter_column('feedback', 'rate_training_sessions', new_column_name='sessions_rating')
    op.alter_column('feedback', 'learner_guide_useful', new_column_name='lguide_useful')
    op.alter_column('feedback', 'confident_to_ride', new_column_name='confident')
    op.alter_column('feedback','trainer_evaluation', new_column_name='trainer_rating')
    op.alter_column('feedback', 'feedback_status', new_column_name='status')

def downgrade() -> None:
    op.alter_column('feedback', 'id', new_column_name='feedback_id')
    op.alter_column('feedback', 'sessions_rating', new_column_name='rate_training_sessions')
    op.alter_column('feedback', 'lguide_useful', new_column_name='learner_guide_useful')
    op.alter_column('feedback', 'confident', new_column_name='confident_to_ride')
    op.alter_column('feedback', 'trainer_rating', new_column_name='trainer_evaluation')
    op.alter_column('feedback', 'status', new_column_name='feedback_status')
