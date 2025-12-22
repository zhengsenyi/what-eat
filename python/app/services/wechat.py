"""
微信小程序登录服务模块

实现微信小程序授权登录的核心逻辑：
1. 通过 code 换取 openid 和 session_key
2. 创建或更新用户信息
3. 生成 JWT token
"""

import httpx
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from datetime import timedelta

from app.config import settings
from app.models.user import User
from app.services.auth import AuthService


class WechatLoginError(Exception):
    """微信登录异常"""
    def __init__(self, errcode: int, errmsg: str):
        self.errcode = errcode
        self.errmsg = errmsg
        super().__init__(f"微信登录失败: [{errcode}] {errmsg}")


class WechatService:
    """微信小程序服务"""
    
    # 微信登录接口
    WECHAT_LOGIN_URL = "https://api.weixin.qq.com/sns/jscode2session"
    
    @staticmethod
    async def code2session(code: str) -> dict:
        """
        通过 code 换取 openid 和 session_key
        
        微信接口文档: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/user-login/code2Session.html
        
        Args:
            code: 微信小程序登录时获取的 code
            
        Returns:
            dict: 包含 openid, session_key, unionid(可选) 的字典
            
        Raises:
            WechatLoginError: 微信接口返回错误时抛出
        """
        params = {
            "appid": settings.WECHAT_APPID,
            "secret": settings.WECHAT_SECRET,
            "js_code": code,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(WechatService.WECHAT_LOGIN_URL, params=params)
            result = response.json()
        
        # 检查是否有错误
        if "errcode" in result and result["errcode"] != 0:
            raise WechatLoginError(
                errcode=result.get("errcode", -1),
                errmsg=result.get("errmsg", "未知错误")
            )
        
        return result
    
    @staticmethod
    def get_user_by_openid(db: Session, openid: str) -> Optional[User]:
        """
        通过 openid 获取用户
        
        Args:
            db: 数据库会话
            openid: 微信用户唯一标识
            
        Returns:
            User 或 None
        """
        return db.query(User).filter(User.openid == openid).first()
    
    @staticmethod
    def create_wechat_user(
        db: Session,
        openid: str,
        unionid: Optional[str] = None,
        nickname: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> User:
        """
        创建微信用户
        
        Args:
            db: 数据库会话
            openid: 微信用户唯一标识
            unionid: 微信开放平台唯一标识（可选）
            nickname: 微信昵称（可选）
            avatar_url: 微信头像URL（可选）
            
        Returns:
            新创建的 User 对象
        """
        user = User(
            openid=openid,
            unionid=unionid,
            nickname=nickname,
            avatar_url=avatar_url
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def update_wechat_user(
        db: Session,
        user: User,
        unionid: Optional[str] = None,
        nickname: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> User:
        """
        更新微信用户信息
        
        Args:
            db: 数据库会话
            user: 用户对象
            unionid: 微信开放平台唯一标识（可选）
            nickname: 微信昵称（可选）
            avatar_url: 微信头像URL（可选）
            
        Returns:
            更新后的 User 对象
        """
        if unionid and not user.unionid:
            user.unionid = unionid
        if nickname is not None:
            user.nickname = nickname
        if avatar_url is not None:
            user.avatar_url = avatar_url
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    async def login(
        db: Session,
        code: str,
        nickname: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> Tuple[User, str, bool]:
        """
        微信小程序登录
        
        完整的登录流程：
        1. 通过 code 换取 openid
        2. 查找或创建用户
        3. 生成 JWT token
        
        Args:
            db: 数据库会话
            code: 微信小程序登录时获取的 code
            nickname: 微信昵称（可选）
            avatar_url: 微信头像URL（可选）
            
        Returns:
            Tuple[User, str, bool]: (用户对象, JWT token, 是否为新用户)
            
        Raises:
            WechatLoginError: 微信接口返回错误时抛出
        """
        # 1. 通过 code 换取 openid
        session_data = await WechatService.code2session(code)
        openid = session_data["openid"]
        unionid = session_data.get("unionid")
        
        # 2. 查找或创建用户
        user = WechatService.get_user_by_openid(db, openid)
        is_new_user = False
        
        if user is None:
            # 新用户，创建账号
            user = WechatService.create_wechat_user(
                db=db,
                openid=openid,
                unionid=unionid,
                nickname=nickname,
                avatar_url=avatar_url
            )
            is_new_user = True
        else:
            # 老用户，更新信息（如果提供了新信息）
            if nickname or avatar_url or (unionid and not user.unionid):
                user = WechatService.update_wechat_user(
                    db=db,
                    user=user,
                    unionid=unionid,
                    nickname=nickname,
                    avatar_url=avatar_url
                )
        
        # 3. 生成 JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        
        return user, access_token, is_new_user