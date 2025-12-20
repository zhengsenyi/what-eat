"""
测试数据库连接
"""
import sys
import os
from pathlib import Path

# 设置控制台编码为 UTF-8
if sys.platform == 'win32':
    os.system('chcp 65001 >nul')

sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from sqlalchemy import create_engine, text

def test_database_connection():
    """测试数据库连接"""
    print("=" * 50)
    print("数据库连接测试")
    print("=" * 50)
    print()
    print(f"数据库URL: {settings.DATABASE_URL}")
    print()

    try:
        # 尝试创建引擎
        engine = create_engine(settings.DATABASE_URL)
        print("[OK] 数据库引擎创建成功")

        # 尝试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("[OK] 数据库连接成功")
            print()
            print("数据库信息:")
            print(f"  - 驱动: {engine.dialect.name}")
            return True

    except Exception as e:
        print("[ERROR] 数据库连接失败！")
        print()
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        print()
        print("可能的原因:")
        print("1. PostgreSQL 服务未启动")
        print("2. 数据库不存在")
        print("3. 用户名或密码错误")
        print("4. 主机地址或端口错误")
        print()
        print("解决方案:")
        print("- 检查 PostgreSQL 服务是否运行")
        print("- 确认 .env 文件中的数据库配置是否正确")
        print("- 运行 init_db.py 初始化数据库")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)
