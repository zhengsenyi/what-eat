from datetime import datetime, date, timezone
from typing import List, Optional
from decimal import Decimal
import random
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.draw_record import DrawRecord
from app.models.food import Food
from app.config import settings


class DrawService:
    @staticmethod
    def get_today_draw_count(db: Session, user_id: int) -> int:
        """获取用户今日已抽取次数"""
        today = date.today()
        count = db.query(DrawRecord).filter(
            DrawRecord.user_id == user_id,
            func.date(DrawRecord.drawn_at) == today
        ).count()
        return count

    @staticmethod
    def get_remaining_times(db: Session, user_id: int) -> int:
        """获取用户今日剩余抽取次数"""
        used_times = DrawService.get_today_draw_count(db, user_id)
        return max(0, settings.DAILY_FREE_TIMES - used_times)

    @staticmethod
    def can_draw(db: Session, user_id: int) -> bool:
        """检查用户今日是否还能抽取"""
        return DrawService.get_remaining_times(db, user_id) > 0

    @staticmethod
    def get_random_food(
        db: Session,
        meal_type: Optional[int] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        category: Optional[str] = None
    ) -> Optional[Food]:
        """
        随机获取一条美食

        Args:
            meal_type: 餐饮类型 1=早餐, 2=午餐, 3=晚餐, 4=夜宵
            min_price: 最小价格
            max_price: 最大价格
            category: 美食分类
        """
        query = db.query(Food)

        # 按餐饮类型筛选
        if meal_type is not None:
            query = query.filter(Food.meal_type == meal_type)

        # 按价格范围筛选（只筛选有价格的食物）
        if min_price is not None or max_price is not None:
            query = query.filter(Food.price.isnot(None))
            if min_price is not None:
                query = query.filter(Food.price >= min_price)
            if max_price is not None:
                query = query.filter(Food.price <= max_price)

        # 按分类筛选
        if category is not None:
            query = query.filter(Food.category == category)

        foods = query.all()
        if not foods:
            return None
        return random.choice(foods)

    @staticmethod
    def create_draw_record(db: Session, user_id: int, food_id: int) -> DrawRecord:
        """创建抽取记录"""
        record = DrawRecord(user_id=user_id, food_id=food_id)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def draw(
        db: Session,
        user_id: int,
        meal_type: Optional[int] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        category: Optional[str] = None
    ) -> tuple[Optional[DrawRecord], str, int]:
        """
        执行抽取操作

        Args:
            meal_type: 餐饮类型 1=早餐, 2=午餐, 3=晚餐, 4=夜宵
            min_price: 最小价格
            max_price: 最大价格
            category: 美食分类

        返回: (抽取记录, 消息, 剩余次数)
        """
        # 检查是否还有抽取次数
        if not DrawService.can_draw(db, user_id):
            return None, "今日抽取次数已用完，明天再来吧！", 0

        # 随机获取美食
        food = DrawService.get_random_food(db, meal_type, min_price, max_price, category)
        if not food:
            remaining = DrawService.get_remaining_times(db, user_id)
            return None, "暂无符合条件的美食数据，请调整筛选条件", remaining

        # 创建抽取记录
        record = DrawService.create_draw_record(db, user_id, food.id)
        remaining = DrawService.get_remaining_times(db, user_id)

        return record, "抽取成功！今天就吃这个吧~", remaining

    @staticmethod
    def get_user_records(db: Session, user_id: int, limit: int = 30) -> List[DrawRecord]:
        """获取用户的抽取记录"""
        return db.query(DrawRecord).filter(
            DrawRecord.user_id == user_id
        ).order_by(DrawRecord.drawn_at.desc()).limit(limit).all()
