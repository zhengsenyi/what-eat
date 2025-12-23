import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.config import settings
from app.routers import user_router, draw_router
from app.openapi_i18n import apply_chinese_descriptions

# 确保静态文件目录存在
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
IMAGES_DIR = os.path.join(STATIC_DIR, "images")
AVATARS_DIR = os.path.join(STATIC_DIR, "avatars")
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(AVATARS_DIR, exist_ok=True)

app = FastAPI(
    title=settings.APP_NAME,
    description="""
## What-Eat API - 今天吃什么？

帮你解决每日灵魂拷问：今天吃什么？

### 功能特性

- 用户注册/登录
- 每日3次免费抽取美食机会
- 查看抽取历史记录

### 认证方式

除了注册和登录接口外，其他接口都需要在请求头中携带 Bearer Token：

```
Authorization: Bearer <your_token>
```
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 注册路由
app.include_router(user_router)
app.include_router(draw_router)


# 全局异常处理 - HTTP异常（包括认证失败等）
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=200,
        content={"code": exc.status_code, "msg": exc.detail, "data": None}
    )


# 全局异常处理 - 参数验证错误
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    if errors:
        first_error = errors[0]
        field = first_error.get("loc", ["", ""])[-1]
        msg = first_error.get("msg", "参数验证失败")
        return JSONResponse(
            status_code=200,
            content={"code": 1, "msg": f"参数错误: {field} - {msg}", "data": None}
        )
    return JSONResponse(
        status_code=200,
        content={"code": 1, "msg": "参数验证失败", "data": None}
    )


# 全局异常处理 - 通用异常
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content={"code": 1, "msg": str(exc) if settings.DEBUG else "服务器内部错误", "data": None}
    )


@app.get("/", tags=["健康检查"])
def root():
    """API 健康检查"""
    return {
        "code": 0,
        "msg": "success",
        "data": {
            "message": "Welcome to What-Eat API!",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/health", tags=["健康检查"])
def health_check():
    """健康检查端点"""
    return {"code": 0, "msg": "success", "data": {"status": "healthy"}}


def custom_openapi():
    """自定义 OpenAPI schema 生成，支持中文化"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version="1.0.0",
        description="""
## What-Eat API - 今天吃什么？

帮你解决每日灵魂拷问：今天吃什么？

### 功能特性

- 用户注册/登录
- 每日3次免费抽取美食机会
- 查看抽取历史记录

### 认证方式

除了注册和登录接口外，其他接口都需要在请求头中携带 Bearer Token：

```
Authorization: Bearer <your_token>
```
        """,
        routes=app.routes,
    )

    # 应用中文化规则
    openapi_schema = apply_chinese_descriptions(openapi_schema)

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# 设置自定义的 OpenAPI schema
app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG
    )
