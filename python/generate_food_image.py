from http import HTTPStatus
import os
import re
import time
import random
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from PIL import Image
import dashscope
from dashscope import ImageSynthesis
import psycopg2

# ===================== 基本配置 =====================

# DashScope API 地址（北京地域）
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

# 1. API Key
# 推荐方式：在 PowerShell 中先执行：
#   $env:DASHSCOPE_API_KEY = "sk-xxxxxxxx"
# 然后这里用环境变量：
# API_KEY = os.getenv("DASHSCOPE_API_KEY")

# 如果你更想直接写死（只在本地用，注意不要提交到仓库），可以这样写：
API_KEY = "sk-12ffbfd3356f459092e025b5f1adb782"

# 2. 图片本地保存目录：static/images
OUTPUT_DIR = os.path.join("static", "images")

# 3. 公网访问的基础域名（务必改成你自己的域名或 IP）
#   举例：
#   - 你线上部署的域名: https://your-domain.com
#   - 本地接口测试: http://127.0.0.1:8000
BASE_URL = "http://8.148.179.255:8000"   # TODO: 换成你的真实域名或地址

# 4. 静态资源在网站中的 URL 前缀（通常和本地路径对应）
#   例如 Flask/Django/Node 通常会把 static 目录映射成 /static
STATIC_URL_PREFIX = "/static/images/"

# 5. 每两次请求之间的间隔（秒），多线程时每个线程都会 sleep
DELAY_SECONDS = 1

# 6. 每次运行最多生成的图片数量；
#    None 表示不限制（会对所有 image_url 为空的记录生成）
MAX_IMAGES = 200  # 测试时先小量，OK 后可改成 None

# 7. 并发线程数（建议 2~5，根据 DashScope 限流情况调整）
MAX_WORKERS = 1

# 8. 生成时 API 的原始尺寸（建议用方图，方便裁剪成 400x400）
API_IMAGE_SIZE = "1328*1328"
TARGET_SIZE = (400, 400)  # 最终输出图片尺寸 400x400

# 9. 数据库配置（当前是 PostgreSQL，使用 psycopg2）
DB_HOST = "127.0.0.1"
DB_PORT = 5432
DB_USER = "postgres"
DB_PASSWORD = "123456"   # TODO: 换成你的密码
DB_NAME = "what_eat"     # TODO: 换成你的数据库名


# ===================== 工具函数 =====================

def safe_filename(name: str) -> str:
    """
    把菜名转成安全的文件名：去掉不合法字符，避免 Windows/Unix 文件名问题。
    """
    name = name.strip()
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    if len(name) > 40:
        name = name[:40]
    return name or "food"


def build_prompt(food: dict) -> str:
    """
    根据菜品信息生成“贴合菜本身”的 prompt，尽量避免所有图片完全一个风格。
    """
    name = food["name"]
    category = food["category"]
    description = food["description"]

    style_candidates = [
        "明亮自然光，俯拍视角",
        "柔和侧光，浅景深特写",
        "暗调氛围，高对比度光影",
        "餐厅桌面场景，中景构图",
        "木质桌面，上帝视角构图",
        "白色背景，简约商务风格",
    ]
    style = random.choice(style_candidates)

    prompt = (
        f"一张关于「{name}」的专业美食摄影高清精修照片。"
        f"菜品类型：{category}。特点：{description}。"
        f"拍摄风格：{style}。"
        f"画面写实、细节丰富、色彩自然，真实光影和质感表现，"
        f"突出食材的纹理和光泽，背景干净不杂乱，适合作为外卖或菜单展示图片。"
        f"不要卡通风格，不要动漫风格，不要插画风格，不要手绘效果，"
        f"不要出现文字水印或 logo。"
    )
    return prompt


def get_resample_method():
    """兼容 Pillow 新旧版本的 LANCZOS 重采样常量。"""
    try:
        return Image.Resampling.LANCZOS  # Pillow >= 10
    except AttributeError:
        return Image.LANCZOS            # Pillow < 10


def build_public_url(filename: str) -> str:
    """
    根据 BASE_URL 和 STATIC_URL_PREFIX 构造公网可访问的图片 URL。
    例如：
      BASE_URL = https://your-domain.com
      STATIC_URL_PREFIX = /static/images/
      filename = 1_宫保鸡丁.png
    => https://your-domain.com/static/images/1_宫保鸡丁.png
    """
    return BASE_URL.rstrip("/") + STATIC_URL_PREFIX + filename


def get_db_connection():
    """
    获取 PostgreSQL 数据库连接（使用 psycopg2）。

    注意：连接和游标不是线程安全的，每个线程应当单独创建和关闭连接。
    """
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    conn.autocommit = True
    return conn


def fetch_foods_without_image(conn, max_images=None):
    """
    从数据库 foods 表中查询 image_url 为空/空串的记录，
    按 id 升序返回 [{id, name, category, description}, ...]。

    :param conn: psycopg2 连接对象（只在主线程中使用）
    :param max_images: 限制最多取多少条（None 表示不限制）
    """
    sql = """
        SELECT id, name, category, description
        FROM foods
        WHERE image_url IS NULL OR image_url = ''
        ORDER BY id ASC
    """
    params = ()
    if max_images is not None:
        sql += " LIMIT %s"
        params = (max_images,)

    foods = []
    with conn.cursor() as cursor:
        cursor.execute(sql, params)
        for row in cursor.fetchall():
            food_id, name, category, description = row
            foods.append({
                "id": food_id,
                "name": name,
                "category": category,
                "description": description,
            })

    return foods


def update_image_url(conn, food_id: int, image_url: str):
    """
    更新数据库 foods 表中对应 id 的 image_url 字段。
    """
    with conn.cursor() as cursor:
        sql = "UPDATE foods SET image_url = %s WHERE id = %s"
        cursor.execute(sql, (image_url, food_id))
        if cursor.rowcount == 0:
            print(f"警告：数据库中未找到 id = {food_id} 的 foods 记录，无法更新 image_url。")
        else:
            print(f"数据库已更新 foods.id = {food_id} 的 image_url。")


def generate_image(prompt: str, out_path: str) -> bool:
    """
    使用 dashscope.ImageSynthesis.call 生成图片，
    然后下载并缩放到 400x400 后保存。
    """
    if not API_KEY:
        print("请先设置环境变量 DASHSCOPE_API_KEY 或在脚本中填入 API_KEY。")
        return False

    try:
        # 1. 调用官方 SDK（同步调用）
        rsp = ImageSynthesis.call(
            api_key=API_KEY,
            model="qwen-image-plus",
            prompt=prompt,
            n=1,
            size=API_IMAGE_SIZE,
            prompt_extend=True,
            watermark=False,
        )

        if rsp.status_code != HTTPStatus.OK:
            print(
                f"调用失败, status_code: {rsp.status_code}, "
                f"code: {getattr(rsp, 'code', None)}, "
                f"message: {getattr(rsp, 'message', None)}"
            )
            return False

        # 2. 取出结果的 URL
        if not rsp.output or not rsp.output.results:
            print("响应中没有 output.results：", rsp)
            return False

        result = rsp.output.results[0]
        url = result.url

        # 3. 下载图片
        img_resp = requests.get(url, timeout=60)
        img_resp.raise_for_status()
        img_bytes = img_resp.content

        # 4. 使用 Pillow 打开并缩放到 400x400
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        resample = get_resample_method()
        img = img.resize(TARGET_SIZE, resample=resample)

        # 5. 保存 PNG
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        img.save(out_path, format="PNG")
        print("saved:", out_path)
        return True

    except Exception as e:
        print("生成失败：", e)
        return False


# ===================== 多线程任务函数 =====================

def process_food_task(food: dict):
    """
    单个线程的任务：

    1. 根据 food 构造 prompt 和文件名；
    2. 调用 DashScope 生成图片并保存本地；
    3. 自己创建数据库连接，更新对应 foods.image_url；
    4. 返回处理结果，方便主线程统计。
    """
    food_id = food["id"]
    name = food["name"]

    try:
        prompt = build_prompt(food)
        filename = f"{safe_filename(name)}.png"
        out_path = os.path.join(OUTPUT_DIR, filename)

        ok = generate_image(prompt, out_path)
        if not ok:
            # 稍微sleep一下，避免连续失败过快打爆API
            time.sleep(DELAY_SECONDS)
            return {
                "food_id": food_id,
                "name": name,
                "success": False,
                "url": None,
                "error": "生成图片失败",
            }

        public_url = build_public_url(filename)

        # 线程内自己开 DB 连接，防止多线程共用连接
        conn = None
        try:
            conn = get_db_connection()
            update_image_url(conn, food_id, public_url)
        finally:
            if conn is not None:
                conn.close()

        # 成功后也 sleep 一下控制频率
        time.sleep(DELAY_SECONDS)

        return {
            "food_id": food_id,
            "name": name,
            "success": True,
            "url": public_url,
            "error": None,
        }

    except Exception as e:
        # 避免异常直接抛出导致线程池崩
        time.sleep(DELAY_SECONDS)
        return {
            "food_id": food_id,
            "name": name,
            "success": False,
            "url": None,
            "error": str(e),
        }


# ===================== 主流程 =====================

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 先用一个连接，在主线程里把需要处理的 foods 列表查出来
    try:
        conn = get_db_connection()
        print("数据库连接成功。")
    except Exception as e:
        print("数据库连接失败，请检查 DB_HOST / DB_USER / DB_PASSWORD / DB_NAME 配置：", e)
        return

    try:
        foods = fetch_foods_without_image(conn, MAX_IMAGES)
        if not foods:
            print("foods 表中没有 image_url 为空的记录，无需生成。")
            return

        total = len(foods)
        print(f"从数据库中获取到 {total} 条 image_url 为空的 foods 记录（按 id 升序）。")

    finally:
        conn.close()
        print("主线程预查询用的数据库连接已关闭。")

    # 多线程并发生成 & 更新
    success = 0
    fail = 0

    print(f"开始多线程生成图片，线程数: {MAX_WORKERS}，目标数量: {total}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 提交任务
        future_to_food = {
            executor.submit(process_food_task, food): food for food in foods
        }

        # as_completed 按完成顺序返回 future
        for idx, future in enumerate(as_completed(future_to_food), start=1):
            food = future_to_food[future]
            food_id = food["id"]
            name = food["name"]

            try:
                result = future.result()
            except Exception as e:
                fail += 1
                print(f"[{idx}/{total}] {name} (id={food_id}) 发生未捕获异常: {e}")
                continue

            if result["success"]:
                success += 1
                print(f"[{idx}/{total}] 成功生成 {name} (id={food_id}) -> {result['url']}")
            else:
                fail += 1
                print(f"[{idx}/{total}] 生成失败 {name} (id={food_id})，原因: {result['error']}")

    print(f"全部任务完成。成功: {success} 张, 失败: {fail} 张, 输出目录: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
