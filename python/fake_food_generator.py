"""
美食数据自动生成脚本
运行此脚本将自动向数据库中插入预定义的美食数据（含价格和图片）
图片使用 Lorem Picsum 服务，保证永久有效
"""

import sys
import os

# 添加项目根目录到 sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Food
from app.database import Base


def get_image_url(seed: str) -> str:
    """生成可靠的图片URL，使用 Lorem Picsum 的 seed 功能"""
    return f"https://picsum.photos/seed/{seed}/400/300"


# 预定义的美食数据（含价格和图片URL）
FOODS_DATA = [
    # ==================== 中餐 ====================
    {"name": "红烧肉", "category": "中餐", "price": 38.00, "description": "肥而不腻，入口即化的经典中式菜肴，色泽红亮，肉质软烂", "image_url": get_image_url("hongshaorou")},
    {"name": "宫保鸡丁", "category": "中餐", "price": 32.00, "description": "鸡肉嫩滑，花生酥脆，酸甜微辣的经典川菜", "image_url": get_image_url("gongbaojiding")},
    {"name": "麻婆豆腐", "category": "中餐", "price": 24.00, "description": "麻辣鲜香，豆腐软嫩的四川名菜，下饭神器", "image_url": get_image_url("mapodoufu")},
    {"name": "糖醋里脊", "category": "中餐", "price": 36.00, "description": "外酥里嫩，酸甜可口，老少皆宜", "image_url": get_image_url("tangculiji")},
    {"name": "鱼香肉丝", "category": "中餐", "price": 28.00, "description": "咸甜酸辣兼备的川菜代表，虽无鱼却有鱼香", "image_url": get_image_url("yuxiangrousi")},
    {"name": "回锅肉", "category": "中餐", "price": 35.00, "description": "肥瘦相间，香辣下饭，四川家常菜之王", "image_url": get_image_url("huiguorou")},
    {"name": "水煮牛肉", "category": "中餐", "price": 48.00, "description": "麻辣鲜烫，牛肉嫩滑，川菜经典", "image_url": get_image_url("shuizhuniurou")},
    {"name": "东坡肉", "category": "中餐", "price": 45.00, "description": "肥而不腻，酥烂香醇，杭州名菜", "image_url": get_image_url("dongporou")},
    {"name": "清蒸鲈鱼", "category": "中餐", "price": 58.00, "description": "鱼肉鲜嫩，原汁原味，清淡养生", "image_url": get_image_url("qingzhengluyu")},
    {"name": "北京烤鸭", "category": "中餐", "price": 128.00, "description": "皮脆肉嫩，肥而不腻的京味名菜", "image_url": get_image_url("beijingkaoya")},
    {"name": "蚂蚁上树", "category": "中餐", "price": 22.00, "description": "粉丝吸满肉末香味，下饭神器", "image_url": get_image_url("mayishangshu")},
    {"name": "干煸四季豆", "category": "中餐", "price": 26.00, "description": "四季豆煸至表皮微皱，配以肉末，香脆可口", "image_url": get_image_url("ganbiansijidou")},
    {"name": "酸菜鱼", "category": "中餐", "price": 52.00, "description": "酸辣开胃，鱼肉鲜嫩，汤底醇厚", "image_url": get_image_url("suancaiyu")},
    {"name": "口水鸡", "category": "中餐", "price": 38.00, "description": "麻辣鲜香，鸡肉嫩滑，川菜凉菜代表", "image_url": get_image_url("koushuiji")},
    {"name": "蒜泥白肉", "category": "中餐", "price": 32.00, "description": "肉片薄如纸，蒜香浓郁，川菜经典凉菜", "image_url": get_image_url("suannibairou")},
    {"name": "辣子鸡", "category": "中餐", "price": 42.00, "description": "外酥里嫩，麻辣鲜香，重庆名菜", "image_url": get_image_url("laziji")},
    {"name": "毛血旺", "category": "中餐", "price": 48.00, "description": "麻辣鲜香，食材丰富，重庆江湖菜", "image_url": get_image_url("maoxuewang")},
    {"name": "夫妻肺片", "category": "中餐", "price": 35.00, "description": "麻辣鲜香，牛肉牛杂切片拌制", "image_url": get_image_url("fuqifeipian")},
    {"name": "剁椒鱼头", "category": "中餐", "price": 68.00, "description": "鲜辣开胃，鱼头肥美，湘菜代表", "image_url": get_image_url("duojiaoyutou")},
    {"name": "松鼠桂鱼", "category": "中餐", "price": 88.00, "description": "外形似松鼠，酸甜可口，苏菜名品", "image_url": get_image_url("songshugui yu")},
    {"name": "叫花鸡", "category": "中餐", "price": 78.00, "description": "荷叶包裹，泥土烤制，皮脆肉嫩", "image_url": get_image_url("jiaohuaji")},
    {"name": "梅菜扣肉", "category": "中餐", "price": 42.00, "description": "梅菜吸收肉汁，肥而不腻，客家名菜", "image_url": get_image_url("meicaikourou")},
    {"name": "白切鸡", "category": "中餐", "price": 48.00, "description": "皮爽肉滑，原汁原味，粤菜经典", "image_url": get_image_url("baiqieji")},
    {"name": "蜜汁叉烧", "category": "中餐", "price": 45.00, "description": "色泽红亮，甜香四溢，港式经典", "image_url": get_image_url("mizhichasao")},
    {"name": "清炒时蔬", "category": "中餐", "price": 18.00, "description": "新鲜时令蔬菜，清淡爽口", "image_url": get_image_url("qingchaoshishu")},
    {"name": "蒜蓉西兰花", "category": "中餐", "price": 22.00, "description": "蒜香浓郁，西兰花脆嫩，健康美味", "image_url": get_image_url("suanrongxilanhua")},
    {"name": "番茄炒蛋", "category": "中餐", "price": 18.00, "description": "家常经典，酸甜可口，营养丰富", "image_url": get_image_url("fanqiechaojidan")},
    {"name": "青椒肉丝", "category": "中餐", "price": 26.00, "description": "青椒脆嫩，肉丝滑嫩，下饭首选", "image_url": get_image_url("qingjiaorosi")},
    {"name": "木须肉", "category": "中餐", "price": 28.00, "description": "鸡蛋木耳肉片，北方家常菜", "image_url": get_image_url("muxurou")},
    {"name": "地三鲜", "category": "中餐", "price": 24.00, "description": "茄子土豆青椒，东北名菜", "image_url": get_image_url("disanxian")},

    # ==================== 西餐 ====================
    {"name": "菲力牛排", "category": "西餐", "price": 128.00, "description": "精选菲力部位，肉质细嫩，入口即化", "image_url": get_image_url("filet-steak")},
    {"name": "西冷牛排", "category": "西餐", "price": 98.00, "description": "带筋牛排，肉香浓郁，口感丰富", "image_url": get_image_url("sirloin-steak")},
    {"name": "肋眼牛排", "category": "西餐", "price": 118.00, "description": "油花分布均匀，多汁鲜嫩", "image_url": get_image_url("ribeye-steak")},
    {"name": "T骨牛排", "category": "西餐", "price": 158.00, "description": "一块牛排两种口感，份量十足", "image_url": get_image_url("tbone-steak")},
    {"name": "意大利肉酱面", "category": "西餐", "price": 42.00, "description": "番茄肉酱浓郁，面条筋道", "image_url": get_image_url("bolognese-pasta")},
    {"name": "奶油培根意面", "category": "西餐", "price": 45.00, "description": "奶油香浓，培根酥脆", "image_url": get_image_url("carbonara-pasta")},
    {"name": "海鲜意大利面", "category": "西餐", "price": 58.00, "description": "新鲜海鲜，蒜香四溢", "image_url": get_image_url("seafood-pasta")},
    {"name": "玛格丽特披萨", "category": "西餐", "price": 48.00, "description": "经典意式披萨，番茄芝士罗勒", "image_url": get_image_url("margherita-pizza")},
    {"name": "培根披萨", "category": "西餐", "price": 52.00, "description": "培根丰富，芝士拉丝", "image_url": get_image_url("bacon-pizza")},
    {"name": "海鲜披萨", "category": "西餐", "price": 62.00, "description": "虾仁鱿鱼蟹肉，海鲜满满", "image_url": get_image_url("seafood-pizza")},
    {"name": "夏威夷披萨", "category": "西餐", "price": 48.00, "description": "菠萝火腿，甜咸交织", "image_url": get_image_url("hawaiian-pizza")},
    {"name": "炸鱼薯条", "category": "西餐", "price": 38.00, "description": "外酥里嫩的英式经典", "image_url": get_image_url("fish-and-chips")},
    {"name": "凯撒沙拉", "category": "西餐", "price": 32.00, "description": "罗马生菜配凯撒酱，清爽开胃", "image_url": get_image_url("caesar-salad")},
    {"name": "希腊沙拉", "category": "西餐", "price": 35.00, "description": "番茄黄瓜羊奶酪，地中海风味", "image_url": get_image_url("greek-salad")},
    {"name": "奶油蘑菇汤", "category": "西餐", "price": 28.00, "description": "浓郁香滑的经典西式汤品", "image_url": get_image_url("mushroom-soup")},
    {"name": "罗宋汤", "category": "西餐", "price": 26.00, "description": "俄式红菜汤，酸甜开胃", "image_url": get_image_url("borscht-soup")},
    {"name": "法式焗蜗牛", "category": "西餐", "price": 68.00, "description": "蒜香黄油烤蜗牛，法式经典前菜", "image_url": get_image_url("escargot")},
    {"name": "烤羊排", "category": "西餐", "price": 88.00, "description": "外焦里嫩，香草风味浓郁", "image_url": get_image_url("lamb-chops")},
    {"name": "香煎三文鱼", "category": "西餐", "price": 78.00, "description": "外皮酥脆，鱼肉鲜嫩多汁", "image_url": get_image_url("pan-seared-salmon")},
    {"name": "烤鸡腿配蔬菜", "category": "西餐", "price": 52.00, "description": "鸡腿多汁，配烤时蔬", "image_url": get_image_url("roasted-chicken")},

    # ==================== 日料 ====================
    {"name": "三文鱼刺身", "category": "日料", "price": 68.00, "description": "新鲜三文鱼切片，入口即化", "image_url": get_image_url("salmon-sashimi")},
    {"name": "金枪鱼刺身", "category": "日料", "price": 88.00, "description": "深海金枪鱼，口感细腻", "image_url": get_image_url("tuna-sashimi")},
    {"name": "刺身拼盘", "category": "日料", "price": 128.00, "description": "多种刺身组合，新鲜美味", "image_url": get_image_url("sashimi-platter")},
    {"name": "寿司拼盘", "category": "日料", "price": 98.00, "description": "多种寿司组合，新鲜美味", "image_url": get_image_url("sushi-platter")},
    {"name": "手握寿司套餐", "category": "日料", "price": 128.00, "description": "师傅现捏，醋饭配新鲜刺身", "image_url": get_image_url("nigiri-sushi")},
    {"name": "三文鱼寿司", "category": "日料", "price": 28.00, "description": "新鲜三文鱼配醋饭", "image_url": get_image_url("salmon-sushi")},
    {"name": "豚骨拉面", "category": "日料", "price": 42.00, "description": "浓郁白汤，叉烧溏心蛋", "image_url": get_image_url("tonkotsu-ramen")},
    {"name": "味噌拉面", "category": "日料", "price": 38.00, "description": "味噌汤底，配料丰富", "image_url": get_image_url("miso-ramen")},
    {"name": "酱油拉面", "category": "日料", "price": 36.00, "description": "清爽酱油汤底，面条筋道", "image_url": get_image_url("shoyu-ramen")},
    {"name": "天妇罗拼盘", "category": "日料", "price": 58.00, "description": "外酥里嫩的日式炸物，虾蔬菜组合", "image_url": get_image_url("tempura-platter")},
    {"name": "炸虾天妇罗", "category": "日料", "price": 48.00, "description": "大虾裹面糊炸制，酥脆可口", "image_url": get_image_url("shrimp-tempura")},
    {"name": "鳗鱼饭", "category": "日料", "price": 78.00, "description": "肥美鳗鱼配甜酱汁，香气四溢", "image_url": get_image_url("unagi-don")},
    {"name": "亲子丼", "category": "日料", "price": 38.00, "description": "鸡肉滑蛋盖饭，家庭味道", "image_url": get_image_url("oyakodon")},
    {"name": "牛丼", "category": "日料", "price": 42.00, "description": "洋葱牛肉配白米饭", "image_url": get_image_url("gyudon")},
    {"name": "日式咖喱饭", "category": "日料", "price": 35.00, "description": "浓郁咖喱配米饭，家常美味", "image_url": get_image_url("japanese-curry")},
    {"name": "照烧鸡肉饭", "category": "日料", "price": 36.00, "description": "甜咸照烧酱汁鸡肉，下饭首选", "image_url": get_image_url("teriyaki-chicken")},
    {"name": "章鱼小丸子", "category": "日料", "price": 22.00, "description": "外脆内软，章鱼鲜美，大阪名物", "image_url": get_image_url("takoyaki")},
    {"name": "日式烧肉", "category": "日料", "price": 98.00, "description": "炭火烤制的优质牛肉，肉香四溢", "image_url": get_image_url("yakiniku")},
    {"name": "味噌汤", "category": "日料", "price": 12.00, "description": "温暖滋润的日式汤品，豆腐海带", "image_url": get_image_url("miso-soup")},
    {"name": "日式炸猪排", "category": "日料", "price": 45.00, "description": "外酥里嫩，配甜辣酱", "image_url": get_image_url("tonkatsu")},
    {"name": "寿喜烧", "category": "日料", "price": 118.00, "description": "甜酱油煮牛肉蔬菜，配生蛋液", "image_url": get_image_url("sukiyaki")},

    # ==================== 韩餐 ====================
    {"name": "韩式炸鸡", "category": "韩餐", "price": 58.00, "description": "外酥里嫩，甜辣酱或蜂蜜酱", "image_url": get_image_url("korean-fried-chicken")},
    {"name": "半半炸鸡", "category": "韩餐", "price": 68.00, "description": "一半原味一半调味，双重享受", "image_url": get_image_url("half-half-chicken")},
    {"name": "芝士炸鸡", "category": "韩餐", "price": 72.00, "description": "炸鸡配浓郁芝士酱", "image_url": get_image_url("cheese-chicken")},
    {"name": "石锅拌饭", "category": "韩餐", "price": 38.00, "description": "锅巴香脆，蔬菜牛肉蛋黄拌匀", "image_url": get_image_url("bibimbap")},
    {"name": "韩式烤五花肉", "category": "韩餐", "price": 78.00, "description": "五花肉配生菜蒜片包食", "image_url": get_image_url("samgyeopsal")},
    {"name": "韩式烤牛肉", "category": "韩餐", "price": 98.00, "description": "腌制牛肉炭火烤制，肉香浓郁", "image_url": get_image_url("bulgogi")},
    {"name": "部队锅", "category": "韩餐", "price": 88.00, "description": "泡面午餐肉年糕泡菜，料足味美", "image_url": get_image_url("budae-jjigae")},
    {"name": "泡菜汤", "category": "韩餐", "price": 32.00, "description": "酸辣开胃的韩式汤品，配米饭", "image_url": get_image_url("kimchi-jjigae")},
    {"name": "大酱汤", "category": "韩餐", "price": 28.00, "description": "韩式大酱汤，豆腐蔬菜", "image_url": get_image_url("doenjang-jjigae")},
    {"name": "嫩豆腐汤", "category": "韩餐", "price": 35.00, "description": "嫩滑豆腐辣汤，海鲜或肉类", "image_url": get_image_url("sundubu-jjigae")},
    {"name": "冷面", "category": "韩餐", "price": 35.00, "description": "冰凉爽口的夏日美食，酸甜汤底", "image_url": get_image_url("naengmyeon")},
    {"name": "辣炒年糕", "category": "韩餐", "price": 28.00, "description": "软糯年糕配甜辣酱，街边小吃", "image_url": get_image_url("tteokbokki")},
    {"name": "参鸡汤", "category": "韩餐", "price": 98.00, "description": "整鸡炖煮，人参糯米，滋补养生", "image_url": get_image_url("samgyetang")},
    {"name": "紫菜包饭", "category": "韩餐", "price": 22.00, "description": "紫菜米饭蔬菜卷，简单美味", "image_url": get_image_url("gimbap")},
    {"name": "韩式炒杂菜", "category": "韩餐", "price": 42.00, "description": "粉丝蔬菜牛肉炒制，配米饭", "image_url": get_image_url("japchae")},
    {"name": "海鲜饼", "category": "韩餐", "price": 38.00, "description": "海鲜蔬菜煎饼，外酥内软", "image_url": get_image_url("haemul-pajeon")},

    # ==================== 小吃 ====================
    {"name": "煎饼果子", "category": "小吃", "price": 12.00, "description": "天津特色早餐，酥脆薄饼配鸡蛋", "image_url": get_image_url("jianbing")},
    {"name": "肉夹馍", "category": "小吃", "price": 15.00, "description": "酥脆白馍夹卤肉，西安名小吃", "image_url": get_image_url("roujiamo")},
    {"name": "小笼包", "category": "小吃", "price": 25.00, "description": "皮薄汁多，鲜香可口，上海特色", "image_url": get_image_url("xiaolongbao")},
    {"name": "生煎包", "category": "小吃", "price": 18.00, "description": "底部金黄酥脆，汤汁丰富", "image_url": get_image_url("shengjian")},
    {"name": "锅贴", "category": "小吃", "price": 16.00, "description": "外皮酥脆，馅料鲜美", "image_url": get_image_url("guotie")},
    {"name": "烧烤拼盘", "category": "小吃", "price": 58.00, "description": "炭火烤制各类肉串，香气四溢", "image_url": get_image_url("bbq-platter")},
    {"name": "羊肉串", "category": "小吃", "price": 8.00, "description": "孜然辣椒烤羊肉，外焦里嫩", "image_url": get_image_url("lamb-skewer")},
    {"name": "烤鸡翅", "category": "小吃", "price": 6.00, "description": "蜜汁烤鸡翅，皮脆肉嫩", "image_url": get_image_url("grilled-wings")},
    {"name": "烤茄子", "category": "小吃", "price": 12.00, "description": "蒜蓉烤茄子，软糯入味", "image_url": get_image_url("grilled-eggplant")},
    {"name": "臭豆腐", "category": "小吃", "price": 10.00, "description": "闻着臭吃着香，长沙特色", "image_url": get_image_url("stinky-tofu")},
    {"name": "凉皮", "category": "小吃", "price": 12.00, "description": "爽滑劲道，酸辣可口，陕西小吃", "image_url": get_image_url("liangpi")},
    {"name": "热干面", "category": "小吃", "price": 12.00, "description": "武汉特色，芝麻酱香浓郁", "image_url": get_image_url("reganmian")},
    {"name": "担担面", "category": "小吃", "price": 15.00, "description": "麻辣鲜香的四川小吃，肉末花生碎", "image_url": get_image_url("dandanmian")},
    {"name": "酸辣粉", "category": "小吃", "price": 15.00, "description": "酸辣开胃的重庆小吃，红薯粉Q弹", "image_url": get_image_url("suanlafen")},
    {"name": "螺蛳粉", "category": "小吃", "price": 18.00, "description": "酸辣鲜爽臭的柳州特色，独特风味", "image_url": get_image_url("luosifen")},
    {"name": "兰州拉面", "category": "小吃", "price": 18.00, "description": "一清二白三红四绿五黄，汤鲜面筋", "image_url": get_image_url("lanzhou-lamian")},
    {"name": "炸酱面", "category": "小吃", "price": 18.00, "description": "北京特色，酱香浓郁配黄瓜丝", "image_url": get_image_url("zhajiangmian")},
    {"name": "饺子", "category": "小吃", "price": 25.00, "description": "皮薄馅大的中式经典，多种口味", "image_url": get_image_url("jiaozi")},
    {"name": "馄饨", "category": "小吃", "price": 18.00, "description": "皮薄馅鲜，汤底清香", "image_url": get_image_url("wonton")},
    {"name": "春卷", "category": "小吃", "price": 15.00, "description": "外皮酥脆，蔬菜肉丝馅", "image_url": get_image_url("spring-roll")},
    {"name": "油条", "category": "小吃", "price": 5.00, "description": "外酥里软的早餐经典，配豆浆", "image_url": get_image_url("youtiao")},
    {"name": "葱油饼", "category": "小吃", "price": 8.00, "description": "层层酥脆，葱香四溢", "image_url": get_image_url("congyoubing")},
    {"name": "手抓饼", "category": "小吃", "price": 10.00, "description": "外酥内软，可加蛋加肠", "image_url": get_image_url("shouzhuabing")},

    # ==================== 甜点 ====================
    {"name": "提拉米苏", "category": "甜点", "price": 38.00, "description": "意式经典，咖啡酒香马斯卡彭芝士", "image_url": get_image_url("tiramisu")},
    {"name": "芝士蛋糕", "category": "甜点", "price": 35.00, "description": "绵密香浓的经典甜点，入口即化", "image_url": get_image_url("cheesecake")},
    {"name": "巧克力熔岩蛋糕", "category": "甜点", "price": 42.00, "description": "外壳酥脆，内心流淌巧克力酱", "image_url": get_image_url("lava-cake")},
    {"name": "马卡龙", "category": "甜点", "price": 28.00, "description": "外酥内软的法式甜点，多种口味", "image_url": get_image_url("macaron")},
    {"name": "舒芙蕾", "category": "甜点", "price": 45.00, "description": "入口即化的法式甜点，现烤现吃", "image_url": get_image_url("souffle")},
    {"name": "双皮奶", "category": "甜点", "price": 18.00, "description": "香滑细腻的广式甜品，奶香浓郁", "image_url": get_image_url("double-skin-milk")},
    {"name": "杨枝甘露", "category": "甜点", "price": 28.00, "description": "芒果西柚的清爽甜品，椰汁打底", "image_url": get_image_url("yangzhi-ganlu")},
    {"name": "红豆汤圆", "category": "甜点", "price": 15.00, "description": "软糯汤圆配红豆汤，甜蜜温暖", "image_url": get_image_url("red-bean-tangyuan")},
    {"name": "蛋挞", "category": "甜点", "price": 8.00, "description": "外酥内嫩的经典点心，奶香蛋香", "image_url": get_image_url("egg-tart")},
    {"name": "葡式蛋挞", "category": "甜点", "price": 10.00, "description": "焦糖表面，奶油馅料浓郁", "image_url": get_image_url("pastel-de-nata")},
    {"name": "千层蛋糕", "category": "甜点", "price": 48.00, "description": "层层薄饼夹奶油，口感丰富", "image_url": get_image_url("mille-crepe")},
    {"name": "抹茶蛋糕", "category": "甜点", "price": 38.00, "description": "抹茶清香，甜而不腻", "image_url": get_image_url("matcha-cake")},
    {"name": "草莓蛋糕", "category": "甜点", "price": 42.00, "description": "新鲜草莓配奶油蛋糕，酸甜可口", "image_url": get_image_url("strawberry-cake")},
    {"name": "冰淇淋", "category": "甜点", "price": 18.00, "description": "多种口味冰淇淋，清凉解暑", "image_url": get_image_url("ice-cream")},
    {"name": "布丁", "category": "甜点", "price": 15.00, "description": "滑嫩Q弹，焦糖奶香", "image_url": get_image_url("pudding")},
    {"name": "甜甜圈", "category": "甜点", "price": 12.00, "description": "松软甜甜圈，多种糖霜口味", "image_url": get_image_url("donut")},

    # ==================== 饮品 ====================
    {"name": "珍珠奶茶", "category": "饮品", "price": 15.00, "description": "Q弹珍珠配香浓奶茶，经典饮品", "image_url": get_image_url("bubble-tea")},
    {"name": "芋泥波波奶茶", "category": "饮品", "price": 18.00, "description": "香芋泥配芋圆波波，浓郁香甜", "image_url": get_image_url("taro-milk-tea")},
    {"name": "杨枝甘露饮品", "category": "饮品", "price": 22.00, "description": "芒果椰汁西柚的清爽组合", "image_url": get_image_url("mango-pomelo")},
    {"name": "柠檬茶", "category": "饮品", "price": 12.00, "description": "清新解腻的港式饮品，冰爽酸甜", "image_url": get_image_url("lemon-tea")},
    {"name": "鲜榨橙汁", "category": "饮品", "price": 18.00, "description": "新鲜橙子现榨，维C满满", "image_url": get_image_url("orange-juice")},
    {"name": "西瓜汁", "category": "饮品", "price": 15.00, "description": "夏日消暑饮品，清甜解渴", "image_url": get_image_url("watermelon-juice")},
    {"name": "冰美式", "category": "饮品", "price": 22.00, "description": "清爽提神的咖啡选择，低卡健康", "image_url": get_image_url("iced-americano")},
    {"name": "拿铁", "category": "饮品", "price": 28.00, "description": "浓缩咖啡配牛奶，丝滑顺口", "image_url": get_image_url("latte")},
    {"name": "卡布奇诺", "category": "饮品", "price": 28.00, "description": "奶泡咖啡经典组合，口感丰富", "image_url": get_image_url("cappuccino")},
    {"name": "摩卡", "category": "饮品", "price": 32.00, "description": "咖啡巧克力牛奶，甜蜜醇厚", "image_url": get_image_url("mocha")},
    {"name": "抹茶拿铁", "category": "饮品", "price": 30.00, "description": "抹茶牛奶，清新回甘", "image_url": get_image_url("matcha-latte")},
    {"name": "可可", "category": "饮品", "price": 22.00, "description": "浓郁巧克力饮品，温暖甜蜜", "image_url": get_image_url("hot-cocoa")},
    {"name": "豆浆", "category": "饮品", "price": 8.00, "description": "传统早餐饮品，营养健康", "image_url": get_image_url("soy-milk")},
    {"name": "酸梅汤", "category": "饮品", "price": 10.00, "description": "传统消暑饮品，酸甜解腻", "image_url": get_image_url("sour-plum-drink")},

    # ==================== 火锅 ====================
    {"name": "四川火锅", "category": "火锅", "price": 88.00, "description": "麻辣鲜香，毛肚黄喉必点，重庆风味", "image_url": get_image_url("sichuan-hotpot")},
    {"name": "潮汕牛肉火锅", "category": "火锅", "price": 108.00, "description": "新鲜牛肉涮清汤，肉质鲜嫩", "image_url": get_image_url("chaoshan-hotpot")},
    {"name": "椰子鸡火锅", "category": "火锅", "price": 98.00, "description": "椰汁清甜，鸡肉鲜嫩，海南风味", "image_url": get_image_url("coconut-chicken-hotpot")},
    {"name": "羊蝎子火锅", "category": "火锅", "price": 118.00, "description": "羊脊骨肉质鲜美，滋补养生", "image_url": get_image_url("lamb-spine-hotpot")},
    {"name": "鱼头火锅", "category": "火锅", "price": 88.00, "description": "鱼头鲜美，汤底浓郁白净", "image_url": get_image_url("fish-head-hotpot")},
    {"name": "菌菇火锅", "category": "火锅", "price": 78.00, "description": "各种菌菇鲜味满满，养生首选", "image_url": get_image_url("mushroom-hotpot")},
    {"name": "番茄火锅", "category": "火锅", "price": 68.00, "description": "酸甜番茄汤底，开胃解腻", "image_url": get_image_url("tomato-hotpot")},
    {"name": "清汤火锅", "category": "火锅", "price": 58.00, "description": "清淡养生，突出食材原味", "image_url": get_image_url("clear-soup-hotpot")},
    {"name": "鸳鸯锅", "category": "火锅", "price": 98.00, "description": "一锅两味，麻辣清汤各取所需", "image_url": get_image_url("yuanyang-hotpot")},

    # ==================== 快餐 ====================
    {"name": "经典牛肉汉堡", "category": "快餐", "price": 28.00, "description": "牛肉饼生菜番茄芝士，经典组合", "image_url": get_image_url("beef-burger")},
    {"name": "双层芝士汉堡", "category": "快餐", "price": 35.00, "description": "双层牛肉双层芝士，满足肉食爱好者", "image_url": get_image_url("double-cheese-burger")},
    {"name": "鸡腿堡", "category": "快餐", "price": 25.00, "description": "香脆鸡腿配生菜沙拉酱", "image_url": get_image_url("chicken-burger")},
    {"name": "炸鸡腿", "category": "快餐", "price": 15.00, "description": "外酥里嫩的快餐经典", "image_url": get_image_url("fried-chicken-leg")},
    {"name": "炸鸡块", "category": "快餐", "price": 18.00, "description": "香酥鸡块，配多种蘸酱", "image_url": get_image_url("chicken-nuggets")},
    {"name": "薯条", "category": "快餐", "price": 12.00, "description": "外酥内软，撒盐或配酱", "image_url": get_image_url("french-fries")},
    {"name": "鸡米花", "category": "快餐", "price": 15.00, "description": "一口一个，酥脆可口", "image_url": get_image_url("popcorn-chicken")},
    {"name": "盖浇饭", "category": "快餐", "price": 22.00, "description": "各种配菜盖在米饭上，快捷美味", "image_url": get_image_url("rice-with-toppings")},
    {"name": "黄焖鸡米饭", "category": "快餐", "price": 25.00, "description": "鸡肉软烂，汤汁浓郁，下饭神器", "image_url": get_image_url("braised-chicken-rice")},
    {"name": "沙县蒸饺", "category": "快餐", "price": 12.00, "description": "沙县小吃招牌，皮薄馅鲜", "image_url": get_image_url("shaxian-dumplings")},
    {"name": "沙县拌面", "category": "快餐", "price": 10.00, "description": "花生酱拌面，简单美味", "image_url": get_image_url("shaxian-noodles")},
    {"name": "沙县扁肉", "category": "快餐", "price": 12.00, "description": "皮薄如纸，汤鲜肉嫩", "image_url": get_image_url("shaxian-wonton")},

    # ==================== 粤式点心 ====================
    {"name": "虾饺", "category": "粤式点心", "price": 28.00, "description": "晶莹剔透，虾肉饱满，粤式点心之王", "image_url": get_image_url("har-gow")},
    {"name": "烧卖", "category": "粤式点心", "price": 25.00, "description": "猪肉虾仁馅，顶部点缀蟹黄", "image_url": get_image_url("siu-mai")},
    {"name": "叉烧包", "category": "粤式点心", "price": 18.00, "description": "松软包子配甜蜜叉烧馅", "image_url": get_image_url("char-siu-bao")},
    {"name": "流沙包", "category": "粤式点心", "price": 22.00, "description": "咸蛋黄流心，甜咸交织", "image_url": get_image_url("liu-sha-bao")},
    {"name": "肠粉", "category": "粤式点心", "price": 20.00, "description": "滑嫩米浆皮包裹虾仁或牛肉", "image_url": get_image_url("cheung-fun")},
    {"name": "凤爪", "category": "粤式点心", "price": 25.00, "description": "豉汁蒸凤爪，软糯入味", "image_url": get_image_url("chicken-feet")},
    {"name": "排骨", "category": "粤式点心", "price": 28.00, "description": "豆豉蒸排骨，肉嫩多汁", "image_url": get_image_url("steamed-ribs")},
    {"name": "萝卜糕", "category": "粤式点心", "price": 18.00, "description": "煎至两面金黄，外酥内软", "image_url": get_image_url("turnip-cake")},
    {"name": "马拉糕", "category": "粤式点心", "price": 15.00, "description": "松软蛋糕，红糖香气", "image_url": get_image_url("ma-lai-gao")},
    {"name": "糯米鸡", "category": "粤式点心", "price": 22.00, "description": "荷叶包裹糯米鸡肉，香气扑鼻", "image_url": get_image_url("lo-mai-gai")},
    {"name": "豉汁蒸排骨", "category": "粤式点心", "price": 28.00, "description": "排骨蒸制，豉汁入味", "image_url": get_image_url("black-bean-ribs")},
    {"name": "鲜虾云吞", "category": "粤式点心", "price": 25.00, "description": "虾肉饱满，汤底鲜美", "image_url": get_image_url("shrimp-wonton")},

    # ==================== 东南亚 ====================
    {"name": "泰式冬阴功", "category": "东南亚", "price": 48.00, "description": "酸辣鲜香，泰国国汤", "image_url": get_image_url("tom-yum")},
    {"name": "绿咖喱鸡", "category": "东南亚", "price": 42.00, "description": "泰式绿咖喱，椰香浓郁", "image_url": get_image_url("green-curry")},
    {"name": "红咖喱牛肉", "category": "东南亚", "price": 48.00, "description": "泰式红咖喱，香辣可口", "image_url": get_image_url("red-curry")},
    {"name": "泰式炒河粉", "category": "东南亚", "price": 35.00, "description": "酸甜可口，配花生碎", "image_url": get_image_url("pad-thai")},
    {"name": "菠萝炒饭", "category": "东南亚", "price": 32.00, "description": "菠萝咖喱风味炒饭", "image_url": get_image_url("pineapple-fried-rice")},
    {"name": "海南鸡饭", "category": "东南亚", "price": 35.00, "description": "鸡肉滑嫩，米饭香糯", "image_url": get_image_url("hainanese-chicken-rice")},
    {"name": "肉骨茶", "category": "东南亚", "price": 45.00, "description": "药材炖排骨，新加坡名菜", "image_url": get_image_url("bak-kut-teh")},
    {"name": "叻沙", "category": "东南亚", "price": 38.00, "description": "椰浆咖喱汤面，马来风味", "image_url": get_image_url("laksa")},
    {"name": "沙爹烤肉", "category": "东南亚", "price": 42.00, "description": "花生酱腌制烤肉串", "image_url": get_image_url("satay")},
    {"name": "越南河粉", "category": "东南亚", "price": 35.00, "description": "清汤牛肉河粉，越南经典", "image_url": get_image_url("pho")},
    {"name": "越南春卷", "category": "东南亚", "price": 28.00, "description": "鲜虾蔬菜透明米皮卷", "image_url": get_image_url("vietnamese-spring-rolls")},
]


def init_food_data(db: Session) -> int:
    """初始化美食数据"""
    # 先删除旧数据
    existing_count = db.query(Food).count()
    if existing_count > 0:
        print(f"删除旧数据 {existing_count} 条...")
        db.query(Food).delete()
        db.commit()

    # 插入新数据
    foods = [Food(**food_data) for food_data in FOODS_DATA]
    db.add_all(foods)
    db.commit()

    print(f"成功插入 {len(foods)} 条美食数据")
    return len(foods)


def main():
    """主函数"""
    print("=" * 60)
    print("美食数据生成器 v3.0")
    print("使用 Lorem Picsum 图片服务，保证图片永久有效")
    print("=" * 60)

    db = SessionLocal()
    try:
        count = init_food_data(db)
        if count > 0:
            # 打印分类统计
            print("\n美食分类统计:")
            print("-" * 40)
            categories = {}
            for food in FOODS_DATA:
                cat = food["category"]
                categories[cat] = categories.get(cat, 0) + 1
            for cat, num in sorted(categories.items(), key=lambda x: -x[1]):
                print(f"  {cat:12} : {num:3} 条")
            print("-" * 40)
            print(f"  {'总计':12} : {len(FOODS_DATA):3} 条")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

    print("=" * 60)
    print("\n图片说明:")
    print("- 使用 Lorem Picsum 服务 (https://picsum.photos)")
    print("- 图片URL格式: https://picsum.photos/seed/{name}/400/300")
    print("- 同一个seed总是返回同一张图片")
    print("- 如需替换为真实图片，请将图片放入 static/images/ 目录")
    print("- 然后更新数据库中的 image_url 字段")
    print("=" * 60)


if __name__ == "__main__":
    main()
