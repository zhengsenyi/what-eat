from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "testuser",
                "password": "password123"
            }
        }


class UserLogin(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "testuser",
                "password": "password123"
            }
        }


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class UserInfoResponse(BaseModel):
    id: int
    username: str
    created_at: datetime
    today_remaining_times: int = Field(..., description="今日剩余抽取次数")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "testuser",
                "created_at": "2024-01-01T00:00:00",
                "today_remaining_times": 2
            }
        }
