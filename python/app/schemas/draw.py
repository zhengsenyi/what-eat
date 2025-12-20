from pydantic import BaseModel, Field
from datetime import datetime
from app.schemas.food import FoodResponse


class DrawResponse(BaseModel):
    success: bool
    message: str
    food: FoodResponse = Field(..., description="抽取到的美食")
    remaining_times: int = Field(..., description="今日剩余抽取次数")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "抽取成功",
                "food": {
                    "id": 1,
                    "name": "红烧肉",
                    "category": "中餐",
                    "description": "肥而不腻，入口即化的经典中式菜肴",
                    "price": 38.00,
                    "image_url": "https://example.com/hongshaorou.jpg"
                },
                "remaining_times": 2
            }
        }


class DrawRecordResponse(BaseModel):
    id: int
    food: FoodResponse
    drawn_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "food": {
                    "id": 1,
                    "name": "红烧肉",
                    "category": "中餐",
                    "description": "肥而不腻，入口即化的经典中式菜肴",
                    "price": 38.00,
                    "image_url": "https://example.com/hongshaorou.jpg"
                },
                "drawn_at": "2024-01-01T12:00:00"
            }
        }
