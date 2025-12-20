from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
from app.database import get_db
from app.schemas.food import FoodResponse
from app.schemas.response import success, error
from app.services.draw import DrawService
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/draw", tags=["抽取美食"])


@router.post("")
def draw_food(
    meal_type: Optional[int] = Query(None, ge=1, le=4, description="餐饮类型: 1=早餐, 2=午餐, 3=晚餐, 4=夜宵"),
    min_price: Optional[Decimal] = Query(None, ge=0, description="最小价格（传此参数则筛选>=该价格的食物）"),
    max_price: Optional[Decimal] = Query(None, ge=0, description="最大价格（传此参数则筛选<=该价格的食物）"),
    category: Optional[str] = Query(None, description="美食分类: 中餐、西餐、日料、韩餐、小吃、甜点、饮品等"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    抽取美食

    - 每日仅有 3 次免费抽取机会
    - 随机抽取一条美食
    - 自动记录抽取历史
    - 支持按餐饮类型、价格范围、分类筛选

    筛选参数（均为可选）：
    - **meal_type**: 餐饮类型 (1=早餐, 2=午餐, 3=晚餐, 4=夜宵)
    - **min_price**: 最小价格，传此参数则筛选 >= 该价格的食物
    - **max_price**: 最大价格，传此参数则筛选 <= 该价格的食物
    - **category**: 美食分类 (中餐、西餐、日料、韩餐、小吃、甜点、饮品等)

    需要在请求头中携带 Bearer Token
    """
    record, message, remaining = DrawService.draw(
        db, current_user.id, meal_type, min_price, max_price, category
    )

    if record is None:
        return error(msg=message)

    return success(
        msg=message,
        data={
            "food": FoodResponse.model_validate(record.food).model_dump(),
            "remaining_times": remaining
        }
    )


@router.get("/records")
def get_draw_records(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取抽取记录

    返回过去 30 条抽取记录

    需要在请求头中携带 Bearer Token
    """
    records = DrawService.get_user_records(db, current_user.id, limit=30)

    return success(
        data={
            "records": [
                {
                    "id": record.id,
                    "food": FoodResponse.model_validate(record.food).model_dump(),
                    "drawn_at": record.drawn_at.isoformat()
                }
                for record in records
            ]
        }
    )
