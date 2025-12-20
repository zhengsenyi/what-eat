"""
OpenAPI 文档中文化工具
提供 OpenAPI 文档的中文化支持
"""


def get_path_summaries() -> dict:
    """获取接口路径中文描述映射"""
    return {
        "/api/user/register": {
            "summary": "用户注册",
            "description": "注册新用户账号，需要提供用户名和密码"
        },
        "/api/user/login": {
            "summary": "用户登录",
            "description": "使用用户名和密码登录，成功后返回访问令牌"
        },
        "/api/user/info": {
            "summary": "获取用户信息",
            "description": "获取当前登录用户的详细信息，包括今日剩余抽取次数"
        },
        "/api/draw": {
            "summary": "抽取美食",
            "description": "随机抽取一道美食，每日限3次免费抽取机会"
        },
        "/api/draw/records": {
            "summary": "获取抽取记录",
            "description": "获取用户最近30条抽取历史记录"
        },
        "/": {
            "summary": "API 根路径",
            "description": "API 健康检查和基本信息"
        },
        "/health": {
            "summary": "健康检查",
            "description": "检查 API 服务运行状态"
        }
    }


def get_field_descriptions() -> dict:
    """获取字段中文描述映射"""
    return {
        # 用户相关
        "id": "唯一标识符",
        "user_id": "用户ID",
        "username": "用户名",
        "password": "密码",
        "nickname": "用户昵称",
        "avatar": "头像URL地址",
        "gender": "性别：0=未知，1=男，2=女",
        "balance": "账户余额（单位：元）",
        "total_spent": "累计消费金额（单位：元）",
        "status": "状态",
        "is_player": "是否为打手身份",
        "created_at": "创建时间",
        "today_remaining_times": "今日剩余抽取次数",

        # 美食相关
        "food_id": "美食ID",
        "name": "美食名称",
        "category": "美食分类",
        "description": "美食描述",
        "image_url": "美食图片URL",

        # 抽取记录相关
        "record_id": "记录ID",
        "drawn_at": "抽取时间",
        "food": "抽中的美食",
        "records": "抽取记录列表",

        # 响应相关
        "success": "操作是否成功",
        "message": "响应消息",
        "data": "响应数据",
        "remaining_times": "剩余次数",

        # Token 相关
        "access_token": "访问令牌",
        "refresh_token": "刷新令牌",
        "token_type": "令牌类型",
    }


def apply_chinese_descriptions(openapi_schema: dict) -> dict:
    """
    为 OpenAPI schema 应用中文描述

    Args:
        openapi_schema: OpenAPI schema 字典

    Returns:
        处理后的 OpenAPI schema
    """
    path_summaries = get_path_summaries()
    field_descriptions = get_field_descriptions()

    # 更新接口路径的 summary 和 description
    if "paths" in openapi_schema:
        for path, path_item in openapi_schema["paths"].items():
            if path in path_summaries:
                path_config = path_summaries[path]
                # 为每个 HTTP 方法添加中文描述
                for method in ["get", "post", "put", "delete", "patch"]:
                    if method in path_item:
                        if "summary" in path_config:
                            path_item[method]["summary"] = path_config["summary"]
                        if "description" in path_config:
                            # 保留原有的 docstring 描述，只在没有时才添加
                            if "description" not in path_item[method] or not path_item[method]["description"]:
                                path_item[method]["description"] = path_config["description"]

            # 为所有接口的参数添加中文描述
            for method in ["get", "post", "put", "delete", "patch"]:
                if method in path_item and "parameters" in path_item[method]:
                    for param in path_item[method]["parameters"]:
                        param_name = param.get("name", "")
                        # 如果参数没有描述，添加中文描述
                        if "description" not in param or not param["description"]:
                            if param_name in field_descriptions:
                                param["description"] = field_descriptions[param_name]

                        # 翻译常见的参数描述
                        if param.get("description"):
                            param["description"] = param["description"].replace(
                                "Query parameter", "查询参数"
                            ).replace(
                                "Path parameter", "路径参数"
                            ).replace(
                                "Header parameter", "请求头参数"
                            )

    # 更新 schemas 中的字段描述
    if "components" in openapi_schema and "schemas" in openapi_schema["components"]:
        schemas = openapi_schema["components"]["schemas"]

        for schema_name, schema_def in schemas.items():
            if "properties" in schema_def:
                for prop_name, prop_def in schema_def["properties"].items():
                    # 添加中文描述
                    if prop_name in field_descriptions and "description" not in prop_def:
                        prop_def["description"] = field_descriptions[prop_name]

    return openapi_schema
