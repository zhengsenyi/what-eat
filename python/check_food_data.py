#!/usr/bin/env python3
"""
食物数据诊断脚本
用于排查抽奖无法抽到数据的问题
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.config import settings

def main():
    print("=" * 60)
    print("食物数据诊断工具")
    print("=" * 60)
    print(f"\n数据库连接: {settings.DATABASE_URL[:50]}...")
    
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # 1. 检查总数据量
        result = conn.execute(text("SELECT COUNT(*) FROM foods"))
        total = result.scalar()
        print(f"\n[1] 食物总数量: {total}")
        
        if total == 0:
            print("\n❌ 错误: 数据库中没有任何食物数据!")
            print("   请先导入食物数据到数据库")
            return
        
        # 2. 检查 meal_type 分布
        print("\n[2] meal_type 分布:")
        result = conn.execute(text("""
            SELECT meal_type, COUNT(*) as cnt 
            FROM foods 
            GROUP BY meal_type 
            ORDER BY meal_type
        """))
        meal_type_map = {1: "早餐", 2: "午餐", 3: "晚餐", 4: "夜宵", None: "未设置"}
        for row in result:
            meal_type, cnt = row
            type_name = meal_type_map.get(meal_type, f"未知({meal_type})")
            print(f"   meal_type={meal_type} ({type_name}): {cnt} 条")
        
        # 3. 检查价格分布
        print("\n[3] 价格分布:")
        result = conn.execute(text("""
            SELECT 
                COUNT(*) FILTER (WHERE price IS NULL) as no_price,
                COUNT(*) FILTER (WHERE price IS NOT NULL) as has_price,
                MIN(price) as min_price,
                MAX(price) as max_price,
                AVG(price)::numeric(10,2) as avg_price
            FROM foods
        """))
        row = result.fetchone()
        print(f"   无价格: {row[0]} 条")
        print(f"   有价格: {row[1]} 条")
        if row[1] > 0:
            print(f"   价格范围: {row[2]} - {row[3]} 元")
            print(f"   平均价格: {row[4]} 元")
        
        # 4. 模拟前端筛选条件查询
        print("\n[4] 模拟前端筛选条件查询:")
        
        # 4.1 只筛选 meal_type=1 (早餐)
        result = conn.execute(text("""
            SELECT COUNT(*) FROM foods WHERE meal_type = 1
        """))
        cnt = result.scalar()
        print(f"   meal_type=1 (早餐): {cnt} 条")
        
        # 4.2 筛选 meal_type=1 且有价格
        result = conn.execute(text("""
            SELECT COUNT(*) FROM foods 
            WHERE meal_type = 1 AND price IS NOT NULL
        """))
        cnt = result.scalar()
        print(f"   meal_type=1 且有价格: {cnt} 条")
        
        # 4.3 筛选 meal_type=1 且价格在 20-80 之间
        result = conn.execute(text("""
            SELECT COUNT(*) FROM foods 
            WHERE meal_type = 1 
            AND price IS NOT NULL 
            AND price >= 20 
            AND price <= 80
        """))
        cnt = result.scalar()
        print(f"   meal_type=1 且价格 20-80: {cnt} 条")
        
        # 4.4 检查各 meal_type 有价格的数量
        print("\n[5] 各 meal_type 有价格的数量:")
        result = conn.execute(text("""
            SELECT meal_type, COUNT(*) as cnt 
            FROM foods 
            WHERE price IS NOT NULL
            GROUP BY meal_type 
            ORDER BY meal_type
        """))
        for row in result:
            meal_type, cnt = row
            type_name = meal_type_map.get(meal_type, f"未知({meal_type})")
            print(f"   meal_type={meal_type} ({type_name}): {cnt} 条")
        
        # 5. 显示一些早餐数据样例
        print("\n[6] 早餐数据样例 (前5条):")
        result = conn.execute(text("""
            SELECT id, name, meal_type, price, category 
            FROM foods 
            WHERE meal_type = 1 
            LIMIT 5
        """))
        rows = result.fetchall()
        if rows:
            for row in rows:
                print(f"   ID={row[0]}, 名称={row[1]}, meal_type={row[2]}, 价格={row[3]}, 分类={row[4]}")
        else:
            print("   ❌ 没有 meal_type=1 的数据!")
        
        # 6. 检查是否所有数据的 meal_type 都是 NULL
        result = conn.execute(text("""
            SELECT COUNT(*) FROM foods WHERE meal_type IS NOT NULL
        """))
        cnt = result.scalar()
        if cnt == 0:
            print("\n" + "=" * 60)
            print("⚠️  警告: 所有食物的 meal_type 都是 NULL!")
            print("   这就是为什么按 meal_type 筛选时找不到数据")
            print("   需要更新数据库中的 meal_type 字段")
            print("=" * 60)
        
        print("\n诊断完成!")


if __name__ == "__main__":
    main()