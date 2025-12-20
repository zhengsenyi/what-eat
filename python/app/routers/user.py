from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin
from app.schemas.response import success, error
from app.services.auth import AuthService
from app.services.draw import DrawService
from app.dependencies import get_current_user
from app.models.user import User
from app.config import settings

router = APIRouter(prefix="/api/user", tags=["用户"])


@router.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册

    - **username**: 用户名（3-50字符）
    - **password**: 密码（至少6字符）
    """
    # 检查用户名是否已存在
    existing_user = AuthService.get_user_by_username(db, user_data.username)
    if existing_user:
        return error(msg="用户名已存在")

    # 创建用户
    user = AuthService.create_user(db, user_data.username, user_data.password)
    return success(
        msg="注册成功",
        data={
            "id": user.id,
            "username": user.username,
            "created_at": user.created_at.isoformat()
        }
    )


@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录

    - **username**: 用户名
    - **password**: 密码
    """
    user = AuthService.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        return error(msg="用户名或密码错误")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    return success(
        msg="登录成功",
        data={
            "access_token": access_token,
            "token_type": "bearer"
        }
    )


@router.get("/info")
def get_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户信息

    需要在请求头中携带 Bearer Token
    """
    remaining_times = DrawService.get_remaining_times(db, current_user.id)

    return success(
        data={
            "id": current_user.id,
            "username": current_user.username,
            "created_at": current_user.created_at.isoformat(),
            "today_remaining_times": remaining_times
        }
    )
