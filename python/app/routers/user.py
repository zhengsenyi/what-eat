from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, WechatLogin, WechatUserInfo
from app.schemas.response import success, error
from app.services.auth import AuthService
from app.services.draw import DrawService
from app.services.wechat import WechatService, WechatLoginError
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


@router.post("/wechat/login")
async def wechat_login(login_data: WechatLogin, db: Session = Depends(get_db)):
    """
    微信小程序登录

    通过微信小程序获取的 code 进行登录，自动创建或关联用户账号。

    - **code**: 微信小程序调用 wx.login() 获取的临时登录凭证

    返回:
    - **access_token**: JWT 访问令牌
    - **token_type**: 令牌类型（bearer）
    - **is_new_user**: 是否为新用户
    - **user**: 用户信息
    """
    try:
        user, access_token, is_new_user = await WechatService.login(
            db=db,
            code=login_data.code
        )
        
        return success(
            msg="登录成功" if not is_new_user else "注册并登录成功",
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "is_new_user": is_new_user,
                "user": {
                    "id": user.id,
                    "openid": user.openid,
                    "nickname": user.nickname,
                    "avatar_url": user.avatar_url,
                    "created_at": user.created_at.isoformat()
                }
            }
        )
    except WechatLoginError as e:
        return error(msg=f"微信登录失败: {e.errmsg}", code=e.errcode)
    except Exception as e:
        return error(msg=f"登录失败: {str(e)}")


@router.put("/wechat/userinfo")
async def update_wechat_userinfo(
    user_info: WechatUserInfo,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新微信用户信息

    用于更新用户的微信昵称和头像等信息。
    需要在请求头中携带 Bearer Token。

    - **nickname**: 微信昵称（可选）
    - **avatar_url**: 微信头像URL（可选）
    """
    # 更新用户信息
    if user_info.nickname is not None:
        current_user.nickname = user_info.nickname
    if user_info.avatar_url is not None:
        current_user.avatar_url = user_info.avatar_url
    
    db.commit()
    db.refresh(current_user)
    
    return success(
        msg="用户信息更新成功",
        data={
            "id": current_user.id,
            "openid": current_user.openid,
            "nickname": current_user.nickname,
            "avatar_url": current_user.avatar_url,
            "created_at": current_user.created_at.isoformat()
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
            "nickname": current_user.nickname,
            "avatar_url": current_user.avatar_url,
            "openid": current_user.openid,
            "created_at": current_user.created_at.isoformat(),
            "today_remaining_times": remaining_times
        }
    )
