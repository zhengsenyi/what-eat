"""
数据库初始化脚本
创建 what_eat 数据库
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# 连接参数
HOST = "localhost"
PORT = 5432
USER = "postgres"
PASSWORD = "postgres"

print(f"尝试连接: host={HOST}, port={PORT}, user={USER}")

try:
    # 连接到默认的 postgres 数据库
    conn = psycopg2.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database="postgres"
    )
except psycopg2.OperationalError as e:
    print(f"连接失败: {e}")
    print("\n请检查:")
    print("1. PostgreSQL 服务是否启动")
    print("2. 用户名和密码是否正确")
    print("3. 端口是否正确 (默认5432)")
    raise
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

cursor = conn.cursor()

# 检查数据库是否存在
cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'what_eat'")
exists = cursor.fetchone()

if not exists:
    cursor.execute("CREATE DATABASE what_eat")
    print("数据库 what_eat 创建成功!")
else:
    print("数据库 what_eat 已存在")

cursor.close()
conn.close()
