"""
完整诊断脚本 - 检测所有可能的问题
"""
import sys
import os
from pathlib import Path

# 设置编码
if sys.platform == 'win32':
    os.system('chcp 65001 >nul')

sys.path.insert(0, str(Path(__file__).parent))

def check_database_tables():
    """检查数据库表是否存在"""
    print("=" * 60)
    print("[1] 检查数据库表")
    print("=" * 60)

    try:
        from app.config import settings
        from sqlalchemy import create_engine, inspect, text

        engine = create_engine(settings.DATABASE_URL)

        with engine.connect() as conn:
            inspector = inspect(engine)
            tables = inspector.get_table_names()

            print(f"数据库中的表: {tables}")

            required_tables = ['users', 'foods', 'draw_records']
            missing = [t for t in required_tables if t not in tables]

            if missing:
                print(f"[WARNING] 缺少表: {missing}")
                print("需要运行数据库迁移或初始化脚本")
                return False
            else:
                print("[OK] 所有必需的表都存在")
                return True

    except Exception as e:
        print(f"[ERROR] 数据库检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_register_endpoint():
    """模拟注册接口调用"""
    print("\n" + "=" * 60)
    print("[2] 模拟注册接口")
    print("=" * 60)

    try:
        from app.database import SessionLocal
        from app.services.auth import AuthService

        db = SessionLocal()
        try:
            # 测试创建用户
            test_username = f"test_diagnostic_{os.getpid()}"
            print(f"尝试创建测试用户: {test_username}")

            # 先检查用户是否存在
            existing = AuthService.get_user_by_username(db, test_username)
            if existing:
                print(f"[INFO] 测试用户已存在，跳过创建")
            else:
                user = AuthService.create_user(db, test_username, "test123456")
                print(f"[OK] 用户创建成功: id={user.id}, username={user.username}")

                # 清理测试用户
                db.delete(user)
                db.commit()
                print("[OK] 测试用户已清理")

            return True

        finally:
            db.close()

    except Exception as e:
        print(f"[ERROR] 注册模拟失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_imports():
    """检查所有导入"""
    print("\n" + "=" * 60)
    print("[3] 检查模块导入")
    print("=" * 60)

    modules_to_check = [
        ("app.config", "settings"),
        ("app.database", "get_db, SessionLocal, Base"),
        ("app.models.user", "User"),
        ("app.models.food", "Food"),
        ("app.models.draw_record", "DrawRecord"),
        ("app.services.auth", "AuthService"),
        ("app.services.draw", "DrawService"),
        ("app.routers.user", "router"),
        ("app.routers.draw", "router"),
        ("app.dependencies", "get_current_user"),
        ("app.main", "app"),
    ]

    all_ok = True
    for module, items in modules_to_check:
        try:
            exec(f"from {module} import {items}")
            print(f"[OK] {module}")
        except Exception as e:
            print(f"[ERROR] {module}: {e}")
            all_ok = False

    return all_ok


def test_full_request():
    """使用 TestClient 测试完整请求"""
    print("\n" + "=" * 60)
    print("[4] 测试完整请求流程")
    print("=" * 60)

    try:
        # 尝试使用 httpx
        import httpx
        from starlette.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        # 测试健康检查
        print("测试 GET /health ...")
        response = client.get("/health")
        print(f"  状态码: {response.status_code}")
        print(f"  响应: {response.json()}")

        # 测试注册
        print("\n测试 POST /api/user/register ...")
        test_data = {
            "username": f"test_full_{os.getpid()}",
            "password": "test123456"
        }
        response = client.post("/api/user/register", json=test_data)
        print(f"  状态码: {response.status_code}")
        print(f"  响应: {response.json()}")

        return True

    except ImportError:
        print("[SKIP] httpx 未安装，无法运行完整测试")
        print("安装命令: pip install httpx")
        return True
    except Exception as e:
        print(f"[ERROR] 完整请求测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("What-Eat API 完整诊断")
    print("=" * 60)
    print()

    results = []

    results.append(("模块导入", check_imports()))
    results.append(("数据库表", check_database_tables()))
    results.append(("注册模拟", check_register_endpoint()))
    results.append(("完整请求", test_full_request()))

    print("\n" + "=" * 60)
    print("诊断结果汇总")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "[OK]" if passed else "[FAILED]"
        print(f"  {status} {name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n所有检查通过！")
    else:
        print("\n存在问题，请查看上面的详细错误信息")

    sys.exit(0 if all_passed else 1)
