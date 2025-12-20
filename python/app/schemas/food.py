from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class FoodResponse(BaseModel):
    id: int
    name: str
    category: str
    meal_type: Optional[int] = None  # 餐饮类型: 1=早餐, 2=午餐, 3=晚餐, 4=夜宵
    description: Optional[str] = None
    price: Optional[Decimal] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "红烧肉",
                "category": "中餐",
                "meal_type": 2,
                "description": "肥而不腻，入口即化的经典中式菜肴",
                "price": 38.00,
                "image_url": "https://example.com/hongshaorou.jpg"
            }
        }
