# 问题修复说明

## 修复的问题

之前 `/api/user/register` 等接口调用时报错，错误发生在 `fastapi/concurrency.py` 的 `contextmanager_in_threadpool`。

### 问题原因

路由函数使用了 `async def` 定义，但数据库操作是同步的（使用 SQLAlchemy + psycopg2）。这导致 FastAPI 在处理同步数据库会话（使用 `yield` 的 `get_db()` 依赖）时出现问题。

### 解决方案

将所有路由函数从 `async def` 改为 `def`（同步函数），因为：
1. 数据库操作是同步的
2. 没有使用异步的数据库驱动
3. FastAPI 可以在线程池中自动处理同步函数

### 修改的文件

1. `app/routers/user.py` - 修改了 3 个路由函数
   - `register` - 用户注册
   - `login` - 用户登录
   - `get_user_info` - 获取用户信息

2. `app/routers/draw.py` - 修改了 2 个路由函数
   - `draw_food` - 抽取美食
   - `get_draw_records` - 获取抽取记录

3. `app/main.py` - 修改了 2 个路由函数
   - `root` - 根路径
   - `health_check` - 健康检查

## 测试验证

### 1. 测试数据库连接
```bash
python test_db.py
# 或
test_db.bat
```

### 2. 测试应用启动
```bash
python test_app.py
```

### 3. 测试 API 接口
```bash
# 先启动服务
start.bat

# 然后在新的命令行窗口中运行测试
python test_api.py
# 或
test_api.bat
```

## 启动服务

```bash
start.bat
```

启动后访问：
- API 文档: http://localhost:8000/docs
- ReDoc 文档: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

## 注意事项

1. 确保 PostgreSQL 服务已启动
2. 确认 `.env` 文件中的数据库配置正确
3. 如果数据库不存在，先运行 `init_db.py` 初始化

## 性能说明

虽然使用同步函数，但 FastAPI 会自动将这些函数放入线程池执行，性能不会有明显下降。如果未来需要更高性能，可以考虑：
- 使用 asyncpg + databases 作为异步数据库驱动
- 使用 SQLAlchemy 的异步版本（async_session）
