from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=True)  # 微信用户可能没有用户名
    hashed_password = Column(String(255), nullable=True)  # 微信用户不需要密码
    
    # 微信小程序相关字段
    openid = Column(String(100), unique=True, index=True, nullable=True)  # 微信用户唯一标识
    unionid = Column(String(100), unique=True, index=True, nullable=True)  # 微信开放平台唯一标识
    nickname = Column(String(100), nullable=True)  # 微信昵称
    avatar_url = Column(String(500), nullable=True)  # 微信头像URL
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    draw_records = relationship("DrawRecord", back_populates="user")
