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


class WechatLogin(BaseModel):
    """微信小程序登录请求"""
    code: str = Field(..., description="微信小程序登录时获取的 code")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "0a1b2c3d4e5f6g7h8i9j"
            }
        }


class WechatUserInfo(BaseModel):
    """微信用户信息（可选，用于更新用户资料）"""
    nickname: Optional[str] = Field(None, max_length=100, description="微信昵称")
    avatar_url: Optional[str] = Field(None, max_length=500, description="微信头像URL")

    class Config:
        json_schema_extra = {
            "example": {
                "nickname": "微信用户",
                "avatar_url": "https://thirdwx.qlogo.cn/mmopen/xxx/132"
            }
        }


class UserResponse(BaseModel):
    id: int
    username: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WechatUserResponse(BaseModel):
    """微信用户响应"""
    id: int
    openid: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "openid": "oXXXX-XXXXXXXXXXXXXXXX",
                "nickname": "微信用户",
                "avatar_url": "https://thirdwx.qlogo.cn/mmopen/xxx/132",
                "created_at": "2024-01-01T00:00:00"
            }
        }


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


class WechatLoginResponse(BaseModel):
    """微信登录响应"""
    access_token: str
    token_type: str = "bearer"
    is_new_user: bool = Field(..., description="是否为新用户")
    user: WechatUserResponse

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "is_new_user": True,
                "user": {
                    "id": 1,
                    "openid": "oXXXX-XXXXXXXXXXXXXXXX",
                    "nickname": "微信用户",
                    "avatar_url": "https://thirdwx.qlogo.cn/mmopen/xxx/132",
                    "created_at": "2024-01-01T00:00:00"
                }
            }
        }


class UserInfoResponse(BaseModel):
    id: int
    username: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    openid: Optional[str] = None
    created_at: datetime
    today_remaining_times: int = Field(..., description="今日剩余抽取次数")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "testuser",
                "nickname": "微信用户",
                "avatar_url": "https://thirdwx.qlogo.cn/mmopen/xxx/132",
                "openid": "oXXXX-XXXXXXXXXXXXXXXX",
                "created_at": "2024-01-01T00:00:00",
                "today_remaining_times": 2
            }
        }
