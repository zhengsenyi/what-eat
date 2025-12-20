"""update meal_type data for existing foods

Revision ID: 004
Revises: 003
Create Date: 2024-12-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 为现有数据设置默认的 meal_type
    # 根据分类或名称推断餐饮类型，这里设置一个通用的默认值 2(午餐)
    # 你可以根据实际需求修改这个逻辑

    # 示例：将所有 meal_type 为 NULL 的记录设置为 2(午餐)
    op.execute("""
        UPDATE foods
        SET meal_type = 2
        WHERE meal_type IS NULL
    """)

    # 如果你想根据分类来设置不同的 meal_type，可以使用类似下面的逻辑：
    # 早餐类（粥、包子、油条等）
    # op.execute("""
    #     UPDATE foods
    #     SET meal_type = 1
    #     WHERE category IN ('早餐', '粥品') OR name LIKE '%粥%' OR name LIKE '%包子%'
    # """)

    # 夜宵类（烧烤、小龙虾等）
    # op.execute("""
    #     UPDATE foods
    #     SET meal_type = 4
    #     WHERE category = '烧烤' OR name LIKE '%烧烤%' OR name LIKE '%小龙虾%'
    # """)


def downgrade() -> None:
    # 回滚时将 meal_type 设为 NULL
    op.execute("""
        UPDATE foods
        SET meal_type = NULL
    """)
