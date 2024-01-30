"""Rename participants table

Revision ID: b462b0c82509
Revises: 9d5e71c04a7f
Create Date: 2024-01-29 21:14:59.507115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b462b0c82509'
down_revision: Union[str, None] = '9d5e71c04a7f'
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
    #op.alter_column('participants', 'participant_created_at', new_column_name='created_on')
    #op.alter_column('participants', 'participant_updated_at', new_column_name='updated_on')
    op.alter_column('participants', 'participant_status', new_column_name='status')
    op.alter_column('participants', 'participant_code', new_column_name='code')
    #op.drop_column('participants', 'participant_created_date')
    #op.drop_column('participants', 'participant_updated_date')

    # Add foreign key constraint for training_location_id
    op.create_foreign_key(
        "fk_training_location",
        "participants",
        "training_locations_list",      
        ["training_location_id"],         
        ["id"],
         ondelete='SET NULL'
                                
    )


def downgrade() -> None:
    #op.add_column('participants', sa.Column('participant_created_date', sa.TIMESTAMP(timezone=True), server_default=sa.func.current_timestamp()))
    #op.add_column('participants', sa.Column('participant_updated_date', sa.TIMESTAMP(timezone=True), server_default=sa.func.current_timestamp()))
    op.alter_column('participants', 'id', new_column_name='participant_id')
    op.alter_column('participants', 'name', new_column_name='participant_name')
    op.alter_column('participants', 'email', new_column_name='participant_email')
    op.alter_column('participants', 'contact', new_column_name='participant_contact')
    op.alter_column('participants', 'address', new_column_name='participant_address')
    op.alter_column('participants', 'age', new_column_name='participant_age')
    op.alter_column('participants', 'gender', new_column_name='participant_gender')
    #op.alter_column('participants', 'created_on', new_column_name='participant_created_at')
    #op.alter_column('participants', 'updated_on', new_column_name='participant_updated_at')
    op.alter_column('participants', 'status', new_column_name='participant_status')
    op.alter_column('participants', 'code', new_column_name='participant_code')

    op.drop_constraint("fk_training_location", "participants", type_="foreignkey")
