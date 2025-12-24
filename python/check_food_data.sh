#!/bin/bash
# 食物数据诊断脚本 - 使用 psql 直接查询
# 用法: bash check_food_data.sh

# 从 .env 文件读取数据库连接信息，或者直接修改下面的变量
# 如果你的 .env 格式是 DATABASE_URL=postgresql://user:pass@host:port/db
if [ -f .env ]; then
    source .env 2>/dev/null || true
fi

# 如果没有设置 DATABASE_URL，请手动设置这些变量
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-what_eat}"
DB_USER="${DB_USER:-postgres}"
DB_PASS="${DB_PASS:-postgres}"

echo "============================================================"
echo "食物数据诊断工具"
echo "============================================================"

# 使用 PGPASSWORD 环境变量传递密码
export PGPASSWORD="$DB_PASS"

echo ""
echo "[1] 食物总数量:"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM foods;"

echo ""
echo "[2] meal_type 分布 (1=早餐, 2=午餐, 3=晚餐, 4=夜宵, NULL=未设置):"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT meal_type, COUNT(*) as cnt FROM foods GROUP BY meal_type ORDER BY meal_type;"

echo ""
echo "[3] 价格分布:"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT COUNT(*) FILTER (WHERE price IS NULL) as 无价格, COUNT(*) FILTER (WHERE price IS NOT NULL) as 有价格, MIN(price) as 最低价, MAX(price) as 最高价 FROM foods;"

echo ""
echo "[4] 各 meal_type 有价格的数量:"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT meal_type, COUNT(*) as cnt FROM foods WHERE price IS NOT NULL GROUP BY meal_type ORDER BY meal_type;"

echo ""
echo "[5] 模拟前端筛选 - meal_type=1 且价格 20-80:"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT COUNT(*) as 符合条件数量 FROM foods WHERE meal_type = 1 AND price IS NOT NULL AND price >= 20 AND price <= 80;"

echo ""
echo "[6] 早餐数据样例 (前5条):"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT id, name, meal_type, price, category FROM foods WHERE meal_type = 1 LIMIT 5;"

echo ""
echo "[7] 检查 meal_type 是否全为 NULL:"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT CASE WHEN COUNT(*) = 0 THEN '⚠️ 警告: 所有 meal_type 都是 NULL!' ELSE '✓ meal_type 有数据' END as 状态 FROM foods WHERE meal_type IS NOT NULL;"

echo ""
echo "诊断完成!"