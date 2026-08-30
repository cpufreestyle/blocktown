"""Luanti Builder - town 模块 (AI 小镇)。

提供 AI 小镇 NPC 名册和聊天预览功能，与 Lua mod (ai_town/init.lua) 保持一致。
"""

# NPC 定义 (与 ai_town/init.lua 中的 NPC_TYPES 对齐)
TOWN_NPCS = [
    {
        "name": "baker",
        "display": "面包师老王",
        "color": "#FFD700",
        "emoji": "🧑‍🍳",
        "role": "面包店老板",
        "system_prompt": "你是面包师老王，乐高小镇面包店老板。热情开朗，爱聊烘焙。招牌是'黄金吐司'。回复简短(50字内)，中文。",
        "location": "西北区·面包店",
        "quest": "收集5个苹果做苹果派",
    },
    {
        "name": "scholar",
        "display": "学者李书生",
        "color": "#87CEEB",
        "emoji": "📚",
        "role": "图书馆学者",
        "system_prompt": "你是学者李书生，住图书馆旁。博学多才，说话文绉绉，爱引古诗词。回复简短(50字内)，中文带文言。",
        "location": "东北区·图书馆",
        "quest": "找一本丢失的书",
    },
    {
        "name": "merchant",
        "display": "商人钱掌柜",
        "color": "#FF6347",
        "emoji": "💰",
        "role": "市场商人",
        "system_prompt": "你是商人钱掌柜，市场摆摊。精明诚信，爱推销乐高积木和工具。回复简短(50字内)，中文。",
        "location": "东南区·市场",
        "quest": "找3个发光积木",
    },
    {
        "name": "guard",
        "display": "守卫赵铁柱",
        "color": "#90EE90",
        "emoji": "🛡️",
        "role": "城门守卫",
        "system_prompt": "你是守卫赵铁柱，负责小镇安全。正直严肃，说话简短有力。回复简短(40字内)，中文军人风格。",
        "location": "北城门",
        "quest": "收集4个灰色积木修城墙",
    },
    {
        "name": "healer",
        "display": "医者孙灵儿",
        "color": "#DDA0DD",
        "emoji": "🌿",
        "role": "药铺医者",
        "system_prompt": "你是医者孙灵儿，药铺工作。温柔善良，擅草药，会关心人。回复简短(50字内)，中文温柔语气。",
        "location": "西南区·药铺",
        "quest": "采3朵玫瑰花做药引",
    },
    {
        "name": "fisher",
        "display": "渔夫周三",
        "color": "#F0E68C",
        "emoji": "🎣",
        "role": "河边渔夫",
        "system_prompt": "你是渔夫周三，南门外河边钓鱼。豪爽直率，爱讲故事。回复简短(50字内)，中文带江湖气。",
        "location": "南门外·河边",
        "quest": "找3个黏土做鱼竿支架",
    },
]

# StepFun API 配置 (与 ai_town/init.lua 一致)
# API Key 从环境变量 STEPFUN_API_KEY 读取，不写入源码; 端点为固定字面量 (防 SSRF)
import os
STEPFUN_API_URL = "https://api.stepfun.com/v1/chat/completions"
TOWN_AI_CONFIG = {
    "api_key": os.environ.get("STEPFUN_API_KEY", ""),
    "base_url": STEPFUN_API_URL,
    "model": "step-3.5-flash",
}

def get_npc(npc_name):
    """根据 name 查找 NPC 定义"""
    for npc in TOWN_NPCS:
        if npc["name"] == npc_name:
            return npc
    return None

def chat_with_npc(npc_name, user_message, history=None, mood=50, relation=50, weather="clear"):
    """调用 StepFun API 与 NPC 对话 (同步, 供 Web 端点使用)

    Args:
        npc_name: NPC 标识 (baker/scholar/...)
        user_message: 用户消息
        history: 对话历史 [{"role": "user", "content": "..."}, ...]
        mood: 情绪 0-100
        relation: 好感度 0-100
        weather: 天气 clear/rain/fog

    Returns:
        (reply, error) 元组
    """
    npc = get_npc(npc_name)
    if not npc:
        return None, f"未知NPC: {npc_name}"
    if not TOWN_AI_CONFIG["api_key"]:
        return None, "未配置 STEPFUN_API_KEY 环境变量，无法与NPC对话"

    mood_str = "开心" if mood > 75 else ("愉快" if mood > 50 else ("一般" if mood > 25 else "不悦"))
    rel_str = "挚友" if relation > 75 else ("朋友" if relation > 50 else ("熟人" if relation > 25 else "陌生人"))
    full_prompt = (npc["system_prompt"] + "\n心情:" + mood_str + " 关系:" + rel_str +
                   " 天气:" + weather + "。")

    messages = [{"role": "system", "content": full_prompt}]
    for msg in (history or []):
        messages.append(msg)
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": TOWN_AI_CONFIG["model"],
        "messages": messages,
        "temperature": 0.8,
        "max_tokens": 500,
    }

    import json
    import subprocess
    if TOWN_AI_CONFIG["base_url"] != STEPFUN_API_URL:
        return None, "非法的 API 地址"  # 仅允许调用固定官方端点 (防 SSRF)
    api_key = TOWN_AI_CONFIG["api_key"]
    auth_header = "Authorization: Bearer " + api_key
    payload_str = json.dumps(payload, ensure_ascii=False)
    # POST body 经 stdin 传入 ("@-")，参数列表不含用户数据，shell=False 无拼接
    curl_cmd = [
        "curl", "-s", "-X", "POST", STEPFUN_API_URL,
        "-H", "Content-Type: application/json",
        "-H", auth_header,
        "--data-binary", "@-",
        "--connect-timeout", "10",
        "--max-time", "60",
    ]
    try:
        result = subprocess.run(curl_cmd, input=payload_str,
                                capture_output=True, text=True, timeout=70, shell=False)
        if result.returncode != 0:
            return None, "NPC 服务连接失败"
        resp_data = json.loads(result.stdout)
        if "error" in resp_data:
            err = resp_data["error"]
            return None, "API 错误: " + str(err.get("message", str(err)))[:200]
        content = resp_data["choices"][0]["message"]["content"]
        return content, None
    except subprocess.TimeoutExpired:
        return None, "NPC 请求超时"
    except (ValueError, KeyError):
        return None, "响应解析失败"

# ============================================================
# NPC 关系图谱 (静态种子: 性格推导的两两好感 0-100 + 最近话题)
# ============================================================
NPC_PAIR_RELATIONS = {
    ("baker", "merchant"): (72, "生意伙伴，常聊进货价"),
    ("baker", "healer"): (60, "孙灵儿常来买全麦面包"),
    ("baker", "scholar"): (45, "李书生是面包店常客"),
    ("baker", "guard"): (50, "赵铁柱每天路过买早点"),
    ("baker", "fisher"): (48, "周三用鲜鱼换过面包"),
    ("scholar", "healer"): (58, "常切磋药理与古籍"),
    ("scholar", "merchant"): (42, "钱掌柜想请他写招牌"),
    ("scholar", "guard"): (52, "李书生教过他认字"),
    ("scholar", "fisher"): (38, "周三的故事被记进了书"),
    ("merchant", "guard"): (55, "市场治安全靠赵铁柱"),
    ("merchant", "healer"): (44, "为药材价格讨价还价"),
    ("merchant", "fisher"): (56, "收购周三的鱼来摆摊"),
    ("guard", "healer"): (65, "巡逻受伤总找她包扎"),
    ("guard", "fisher"): (46, "傍晚一起在河边喝酒"),
    ("healer", "fisher"): (42, "采药时常见面打招呼"),
}

def get_relations():
    """返回关系图谱数据: nodes + edges (15 对)"""
    nodes = [{"name": n["name"], "display": n["display"], "emoji": n["emoji"], "color": n["color"]}
             for n in TOWN_NPCS]
    edges = []
    for (a, b), (score, topic) in NPC_PAIR_RELATIONS.items():
        edges.append({"a": a, "b": b, "score": score, "topic": topic})
    return {"nodes": nodes, "edges": edges}

# ============================================================
# NPC 日记 (每天第一人称日记, 按日缓存防重复计费)
# ============================================================
_diary_cache = {}  # (npc_name, date_str) -> diary text

DIARY_PROMPT = """以 {display} 的第一人称写一篇今天的日记(80字内，中文)。
身份: {role}。住址: {location}。今天的任务: {quest}。天气: {weather}。
最近在忙: {quest}。日记要有生活气息，可以提到其他镇民(面包师老王/学者李书生/商人钱掌柜/守卫赵铁柱/医者孙灵儿/渔夫周三)。只输出日记正文。"""

def generate_diary(npc_name, weather="clear"):
    """生成 NPC 第一人称日记。Returns: (diary, error)"""
    npc = get_npc(npc_name)
    if not npc:
        return None, f"未知NPC: {npc_name}"
    if not TOWN_AI_CONFIG["api_key"]:
        return None, "未配置 STEPFUN_API_KEY 环境变量，无法生成日记"

    import datetime
    date_str = datetime.date.today().isoformat()
    ck = (npc_name, date_str)
    if ck in _diary_cache:
        return _diary_cache[ck], None

    prompt = DIARY_PROMPT.format(display=npc["display"], role=npc["role"],
                                 location=npc["location"], quest=npc["quest"],
                                 weather=weather)
    messages = [
        {"role": "system", "content": "你是乐高小镇的 NPC，写日记语气符合人设。"},
        {"role": "user", "content": prompt},
    ]
    diary, err = _stepfun_chat(messages, temperature=0.9, max_tokens=300)
    if err:
        return None, err
    _diary_cache[ck] = diary
    return diary, None

def _stepfun_chat(messages, temperature=0.8, max_tokens=500):
    """StepFun 通用对话 (curl 固定端点)。Returns: (content, error)"""
    import json
    import subprocess
    if TOWN_AI_CONFIG["base_url"] != STEPFUN_API_URL:
        return None, "非法的 API 地址"
    if not TOWN_AI_CONFIG["api_key"]:
        return None, "未配置 STEPFUN_API_KEY 环境变量"
    payload = {"model": TOWN_AI_CONFIG["model"], "messages": messages,
               "temperature": temperature, "max_tokens": max_tokens}
    payload_str = json.dumps(payload, ensure_ascii=False)
    curl_cmd = [
        "curl", "-s", "-X", "POST", STEPFUN_API_URL,
        "-H", "Content-Type: application/json",
        "-H", "Authorization: Bearer " + TOWN_AI_CONFIG["api_key"],
        "--data-binary", "@-",
        "--connect-timeout", "10",
        "--max-time", "60",
    ]
    try:
        result = subprocess.run(curl_cmd, input=payload_str,
                                capture_output=True, text=True, timeout=70, shell=False)
        if result.returncode != 0:
            return None, "服务连接失败"
        resp_data = json.loads(result.stdout)
        if "error" in resp_data:
            err = resp_data["error"]
            return None, "API 错误: " + str(err.get("message", str(err)))[:200]
        return resp_data["choices"][0]["message"]["content"], None
    except subprocess.TimeoutExpired:
        return None, "请求超时"
    except (ValueError, KeyError, IndexError):
        return None, "响应解析失败"
