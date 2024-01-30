"""Rename trainer table

Revision ID: a5adc765449c
Revises: b462b0c82509
Create Date: 2024-01-29 21:44:45.761162

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5adc765449c'
down_revision: Union[str, None] = 'b462b0c82509'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():  
    op.execute('ALTER TABLE public.trainer RENAME COLUMN trainer_id TO id')
    op.execute('ALTER TABLE public.trainer RENAME COLUMN trainer_name TO name')
    op.execute('ALTER TABLE public.trainer RENAME COLUMN trainer_email TO email')
    op.execute('ALTER TABLE public.trainer RENAME COLUMN trainer_contact TO contact')
    op.execute('ALTER TABLE public.trainer RENAME COLUMN trainer_address TO address')
    op.execute('ALTER TABLE public.trainer RENAME COLUMN trainer_age TO age')
    op.execute('ALTER TABLE public.trainer RENAME COLUMN trainer_gender TO gender')
    op.execute('ALTER TABLE public.trainer RENAME COLUMN trainer_education TO education')
    op.execute('ALTER TABLE public.trainer RENAME COLUMN trainer_aadhar_no TO aadhar_no')
    op.execute('ALTER TABLE public.trainer RENAME COLUMN trainer_training_completion_date TO training_completion')
    op.execute('ALTER TABLE public.trainer RENAME COLUMN trainer_status TO status')
    op.execute('ALTER TABLE public.trainer RENAME COLUMN trainer_code TO code')
    op.execute('ALTER TABLE public.trainer RENAME COLUMN trainer_language TO language')
   # pass
   
def downgrade() -> None:    
    # Rename the columns back to their original names
    op.execute('ALTER TABLE public.trainer RENAME COLUMN id TO trainer_id')
    op.execute('ALTER TABLE public.trainer RENAME COLUMN name TO trainer_name')
    op.execute('ALTER TABLE public.trainer RENAME COLUMN email TO trainer_email')
    op.execute('ALTER TABLE public.trainer RENAME COLUMN contact TO trainer_contact')
    op.execute('ALTER TABLE public.trainer RENAME COLUMN address TO trainer_address')
    op.execute('ALTER TABLE public.trainer RENAME COLUMN age TO trainer_age')
    op.execute('ALTER TABLE public.trainer RENAME COLUMN gender TO trainer_gender')
    op.execute('ALTER TABLE public.trainer RENAME COLUMN education TO trainer_education')
    op.execute('ALTER TABLE public.trainer RENAME COLUMN aadhar_no TO trainer_aadhar_no')
    op.execute('ALTER TABLE public.trainer RENAME COLUMN training_completion TO trainer_training_completion_date')
    op.execute('ALTER TABLE public.trainer RENAME COLUMN status TO trainer_status')
    op.execute('ALTER TABLE public.trainer RENAME COLUMN code TO trainer_code')
    #pass

    