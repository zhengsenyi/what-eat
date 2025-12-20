"""
测试 API 接口
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查接口"""
    print("=" * 50)
    print("测试健康检查接口")
    print("=" * 50)
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_register():
    """测试注册接口"""
    print("\n" + "=" * 50)
    print("测试注册接口")
    print("=" * 50)
    try:
        data = {
            "username": "testuser123",
            "password": "password123"
        }
        print(f"请求数据: {json.dumps(data, indent=2)}")

        response = requests.post(
            f"{BASE_URL}/api/user/register",
            json=data,
            timeout=5
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        return response.status_code in [200, 201, 400]  # 400 表示用户已存在也是正常的
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

def test_login():
    """测试登录接口"""
    print("\n" + "=" * 50)
    print("测试登录接口")
    print("=" * 50)
    try:
        data = {
            "username": "testuser123",
            "password": "password123"
        }
        print(f"请求数据: {json.dumps(data, indent=2)}")

        response = requests.post(
            f"{BASE_URL}/api/user/login",
            json=data,
            timeout=5
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"\n获取到 Token: {token[:50]}...")
            return True, token
        return False, None
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_user_info(token):
    """测试获取用户信息接口"""
    print("\n" + "=" * 50)
    print("测试获取用户信息接口")
    print("=" * 50)
    try:
        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.get(
            f"{BASE_URL}/api/user/info",
            headers=headers,
            timeout=5
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始测试 API 接口...")
    print("请确保服务已启动（运行 start.bat）\n")

    # 测试健康检查
    if not test_health():
        print("\n[ERROR] 健康检查失败，请确保服务已启动")
        sys.exit(1)

    # 测试注册
    if not test_register():
        print("\n[ERROR] 注册接口测试失败")
        sys.exit(1)

    # 测试登录
    success, token = test_login()
    if not success:
        print("\n[ERROR] 登录接口测试失败")
        sys.exit(1)

    # 测试获取用户信息
    if not test_user_info(token):
        print("\n[ERROR] 获取用户信息接口测试失败")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("[SUCCESS] 所有接口测试通过！")
    print("=" * 50)
