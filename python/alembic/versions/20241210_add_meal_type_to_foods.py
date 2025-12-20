"""add meal_type to foods

Revision ID: 002
Revises: 001
Create Date: 2024-12-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add meal_type column to foods table
    op.add_column('foods', sa.Column('meal_type', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_foods_meal_type'), 'foods', ['meal_type'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_foods_meal_type'), table_name='foods')
    op.drop_column('foods', 'meal_type')
