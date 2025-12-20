from sqlalchemy import Column, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class DrawRecord(Base):
    __tablename__ = "draw_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    food_id = Column(Integer, ForeignKey("foods.id"), nullable=False)
    drawn_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="draw_records")
    food = relationship("Food", back_populates="draw_records")
