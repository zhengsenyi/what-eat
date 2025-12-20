"""initial migration

Revision ID: 001
Revises:
Create Date: 2024-12-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create foods table
    op.create_table(
        'foods',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_foods_id'), 'foods', ['id'], unique=False)

    # Create draw_records table
    op.create_table(
        'draw_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('food_id', sa.Integer(), nullable=False),
        sa.Column('drawn_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['food_id'], ['foods.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_draw_records_id'), 'draw_records', ['id'], unique=False)
    op.create_index(op.f('ix_draw_records_user_id'), 'draw_records', ['user_id'], unique=False)
    op.create_index(op.f('ix_draw_records_drawn_at'), 'draw_records', ['drawn_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_draw_records_drawn_at'), table_name='draw_records')
    op.drop_index(op.f('ix_draw_records_user_id'), table_name='draw_records')
    op.drop_index(op.f('ix_draw_records_id'), table_name='draw_records')
    op.drop_table('draw_records')

    op.drop_index(op.f('ix_foods_id'), table_name='foods')
    op.drop_table('foods')

    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
