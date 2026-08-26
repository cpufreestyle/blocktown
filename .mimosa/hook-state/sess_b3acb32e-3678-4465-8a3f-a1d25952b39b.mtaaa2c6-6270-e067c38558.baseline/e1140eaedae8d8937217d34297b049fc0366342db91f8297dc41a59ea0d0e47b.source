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
TOWN_AI_CONFIG = {
    "api_key": "34h3kvASCJOJDoGu2g4xwRkwlYeqstFYDk6Or0RWfFWxVrgiL14QijTQ04Usoxzyw",
    "base_url": "https://api.stepfun.com/v1/chat/completions",
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
    import urllib.request
    import urllib.error

    npc = get_npc(npc_name)
    if not npc:
        return None, f"未知NPC: {npc_name}"

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
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        TOWN_AI_CONFIG["base_url"],
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + TOWN_AI_CONFIG["api_key"],
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            content = result["choices"][0]["message"]["content"]
            return content, None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}"
    except Exception as e:
        return None, str(e)
