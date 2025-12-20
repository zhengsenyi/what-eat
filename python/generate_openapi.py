"""
自动生成 OpenAPI 文档脚本
运行方式: python generate_openapi.py
"""
import json
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from fastapi.openapi.utils import get_openapi
from app.main import app
from app.openapi_i18n import apply_chinese_descriptions


def add_request_examples(openapi_schema: dict) -> dict:
    """为请求模型添加示例数据"""

    # 请求模型示例数据映射
    request_examples = {
        "WeChatLoginRequest": {
            "code": "081234567890abcdef",
            "nickname": "游戏玩家",
            "avatar": "https://example.com/avatar.jpg",
            "gender": 1
        },
        "RefreshTokenRequest": {
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        },
        "Body_bind_phone_api_v1_auth_bind_phone_post": {
            "phone": "13800138000"
        },
        "UserUpdateRequest": {
            "nickname": "新昵称",
            "avatar": "https://example.com/new-avatar.jpg",
            "gender": 1
        },
        "GameCreateRequest": {
            "name": "英雄联盟",
            "code": "lol",
            "icon": "https://example.com/lol-icon.png",
            "description": "5V5竞技游戏",
            "is_hot": True,
            "sort_order": 100
        },
        "GameUpdateRequest": {
            "name": "英雄联盟",
            "icon": "https://example.com/lol-icon-new.png",
            "description": "5V5竞技游戏 - 更新版",
            "is_hot": True,
            "sort_order": 100
        },
        "PlayerApplyRequest": {
            "real_name": "张三",
            "id_card": "110101199001011234",
            "introduction": "擅长射手英雄，5年游戏经验",
            "tags": ["稳定", "技术好", "脾气好"]
        },
        "PlayerUpdateRequest": {
            "introduction": "擅长射手和辅助英雄，5年游戏经验",
            "tags": ["稳定", "技术好", "脾气好", "声音好听"],
            "max_daily_orders": 10
        },
        "OnlineStatusRequest": {
            "is_online": True
        },
        "PlayerAuditRequest": {
            "action": "approve",
            "reason": None
        },
        "SkillCreateRequest": {
            "game_id": "550e8400-e29b-41d4-a716-446655440000",
            "rank": "王者",
            "win_rate": 65.5,
            "hero_pool": ["后羿", "鲁班七号", "狄仁杰"],
            "price_per_hour": 50.0,
            "is_primary": True
        },
        "SkillUpdateRequest": {
            "rank": "荣耀王者",
            "win_rate": 68.0,
            "hero_pool": ["后羿", "鲁班七号", "狄仁杰", "马可波罗"],
            "price_per_hour": 60.0,
            "is_primary": True
        },
        "OrderCreateRequest": {
            "player_id": "550e8400-e29b-41d4-a716-446655440001",
            "game_id": "550e8400-e29b-41d4-a716-446655440000",
            "duration": 2,
            "start_time": "2024-01-20T14:00:00"
        },
        "CancelOrderRequest": {
            "reason": "临时有事，无法继续"
        },
        "ReviewCreateRequest": {
            "order_id": "550e8400-e29b-41d4-a716-446655440002",
            "rating": 5,
            "content": "打手技术很好，态度友好，非常满意！",
            "tags": ["技术好", "态度好", "准时"],
            "is_anonymous": False
        },
        "ReviewReplyRequest": {
            "reply": "感谢您的好评，期待下次合作！"
        },
        "RechargeRequest": {
            "amount": 100.0,
            "payment_method": "wechat"
        }
    }

    if "components" in openapi_schema and "schemas" in openapi_schema["components"]:
        schemas = openapi_schema["components"]["schemas"]

        for schema_name, schema_def in schemas.items():
            # 为请求模型添加example
            if schema_name in request_examples:
                schema_def["example"] = request_examples[schema_name]

    return openapi_schema


def generate_openapi_json():
    """生成 OpenAPI JSON 文档"""

    # 生成基础 OpenAPI schema
    openapi_schema = get_openapi(
        title="吃啥盲盒后端API",
        version="1.0.0",
        description="基于Python FastAPI开发的吃啥盲盒系统API文档",
        routes=app.routes,
        contact={
            "name": "Delta Team"
        }
    )

    # 应用中文化规则
    openapi_schema = apply_chinese_descriptions(openapi_schema)

    # 添加请求示例
    openapi_schema = add_request_examples(openapi_schema)

    # 添加服务器配置（可选）
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "本地开发环境"
        },
        {
            "url": "https://api.example.com",
            "description": "生产环境"
        }
    ]

    # 保存到文件
    output_file = Path(__file__).parent / "吃啥盲盒.openapi.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, ensure_ascii=False, indent=2)

    print(f"[SUCCESS] OpenAPI 文档已生成: {output_file}")
    print(f"[INFO] 包含 {len(openapi_schema.get('paths', {}))} 个接口")
    print(f"[INFO] 包含 {len(openapi_schema.get('components', {}).get('schemas', {}))} 个数据模型")


if __name__ == "__main__":
    try:
        generate_openapi_json()
    except Exception as e:
        print(f"[ERROR] 生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
