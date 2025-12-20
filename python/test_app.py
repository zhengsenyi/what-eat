"""
测试应用启动
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_app_startup():
    """测试应用能否正常启动"""
    print("=" * 50)
    print("应用启动测试")
    print("=" * 50)
    print()

    try:
        print("[1/3] 导入应用...")
        from app.main import app
        print("[OK] 应用导入成功")

        print()
        print("[2/3] 测试 OpenAPI schema 生成...")
        schema = app.openapi()
        print(f"[OK] OpenAPI schema 生成成功，包含 {len(schema.get('paths', {}))} 个接口")

        print()
        print("[3/3] 检查路由...")
        routes = [route for route in app.routes]
        print(f"[OK] 共有 {len(routes)} 个路由")

        print()
        print("=" * 50)
        print("所有测试通过！应用可以正常启动")
        print("=" * 50)
        return True

    except Exception as e:
        print(f"[ERROR] 测试失败！")
        print()
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        print()
        import traceback
        print("完整错误堆栈:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_app_startup()
    sys.exit(0 if success else 1)
