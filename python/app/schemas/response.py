from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """统一API响应结构"""
    code: int = 0
    msg: str = "success"
    data: Optional[T] = None

    class Config:
        json_schema_extra = {
            "example": {
                "code": 0,
                "msg": "success",
                "data": {}
            }
        }


def success(data: T = None, msg: str = "success") -> dict:
    """成功响应"""
    return {"code": 0, "msg": msg, "data": data}


def error(msg: str, code: int = 1, data: T = None) -> dict:
    """错误响应"""
    return {"code": code, "msg": msg, "data": data}
