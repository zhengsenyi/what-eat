"""add wechat fields to users

Revision ID: 005
Revises: 004
Create Date: 2024-12-22 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """添加微信小程序相关字段到 users 表"""
    
    # 添加微信相关字段
    op.add_column('users', sa.Column('openid', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('unionid', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('nickname', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('avatar_url', sa.String(500), nullable=True))
    
    # 创建唯一索引
    op.create_index('ix_users_openid', 'users', ['openid'], unique=True)
    op.create_index('ix_users_unionid', 'users', ['unionid'], unique=True)
    
    # 修改 username 和 hashed_password 为可空（微信用户不需要这些字段）
    op.alter_column('users', 'username',
                    existing_type=sa.String(50),
                    nullable=True)
    op.alter_column('users', 'hashed_password',
                    existing_type=sa.String(255),
                    nullable=True)


def downgrade() -> None:
    """回滚：移除微信相关字段"""
    
    # 恢复 username 和 hashed_password 为非空
    # 注意：如果有微信用户数据，需要先处理这些数据
    op.alter_column('users', 'username',
                    existing_type=sa.String(50),
                    nullable=False)
    op.alter_column('users', 'hashed_password',
                    existing_type=sa.String(255),
                    nullable=False)
    
    # 删除索引
    op.drop_index('ix_users_unionid', table_name='users')
    op.drop_index('ix_users_openid', table_name='users')
    
    # 删除微信相关字段
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'nickname')
    op.drop_column('users', 'unionid')
    op.drop_column('users', 'openid')