from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.config import settings

# 创建数据库引擎，添加连接池配置
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,  # 连接池大小
    max_overflow=10,  # 超出pool_size后最多可以创建的连接数
    pool_timeout=30,  # 获取连接的超时时间（秒）
    pool_recycle=1800,  # 连接回收时间（秒），防止连接被数据库服务器关闭
    pool_pre_ping=True,  # 每次使用连接前先ping一下，检测连接是否有效
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
