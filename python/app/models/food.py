from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric, func
from sqlalchemy.orm import relationship
from app.database import Base


class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # 中餐、西餐、日料、韩餐、小吃、甜点、饮品
    meal_type = Column(Integer, nullable=True, index=True)  # 餐饮类型: 1=早餐, 2=午餐, 3=晚餐, 4=夜宵
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=True)  # 价格，保留2位小数
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    draw_records = relationship("DrawRecord", back_populates="food")
