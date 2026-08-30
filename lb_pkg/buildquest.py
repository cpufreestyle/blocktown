"""Luanti Builder - buildquest 模块 (建筑挑战任务)。

Server 持有任务列表与轮换状态（单一来源）：Web UI 拉取展示，Lua mod 每分钟
拉取任务 spec 并在游戏内自动验收，完成后 POST done 轮换下一任务。
任务为静态模板 (MVP)，不走 LLM 生成。
"""

BUILD_QUESTS = [
    {
        "id": "lighthouse",
        "title": "灯塔",
        "emoji": "🗼",
        "patron": "merchant",  # NPC name, 与 TOWN_NPCS/ai_town NPC_TYPES 对齐
        "prompt_hint": "在广场边造一座灯塔，灰色砖为主体，顶部有发光积木做灯室",
        "requirements": [
            {"node": "my_first_mod:brick_gray", "count": 30, "label": "灰砖"},
            {"node": "my_first_mod:brick_glow", "count": 5, "label": "发光积木"},
        ],
        "reward_reputation": 15,
    },
    {
        "id": "fountain",
        "title": "喷泉",
        "emoji": "⛲",
        "patron": "healer",
        "prompt_hint": "在广场造一座圆形喷泉，白色砖砌池壁，蓝色砖做水面装饰",
        "requirements": [
            {"node": "my_first_mod:brick_white", "count": 25, "label": "白砖"},
            {"node": "my_first_mod:brick_blue", "count": 15, "label": "蓝砖"},
        ],
        "reward_reputation": 15,
    },
    {
        "id": "watchtower",
        "title": "瞭望塔",
        "emoji": "🏰",
        "patron": "guard",
        "prompt_hint": "在城门附近造一座高耸的瞭望塔，灰色砖主体，顶部用红色砖做旗帜标志",
        "requirements": [
            {"node": "my_first_mod:brick_gray", "count": 40, "label": "灰砖"},
            {"node": "my_first_mod:brick_red", "count": 10, "label": "红砖"},
        ],
        "reward_reputation": 15,
    },
    {
        "id": "garden_pavilion",
        "title": "花园凉亭",
        "emoji": "🌸",
        "patron": "scholar",
        "prompt_hint": "在图书馆旁造一座花园凉亭，粉色砖做花架，绿色砖做藤蔓立柱",
        "requirements": [
            {"node": "my_first_mod:brick_pink", "count": 20, "label": "粉砖"},
            {"node": "my_first_mod:brick_green", "count": 15, "label": "绿砖"},
        ],
        "reward_reputation": 15,
    },
]

# 进程内轮换状态（重启后回到 0，可接受：任务为静态循环，无持久化必要）
_quest_index = 0


def current_quest():
    """当前任务 + patron 展示信息（供 Web 与 Lua 共用一份结构）。"""
    from .town import TOWN_NPCS
    quest = BUILD_QUESTS[_quest_index]
    patron = next((n for n in TOWN_NPCS if n["name"] == quest["patron"]), None)
    return {
        "id": quest["id"],
        "title": quest["title"],
        "emoji": quest["emoji"],
        "prompt_hint": quest["prompt_hint"],
        "requirements": [
            {"node": r["node"], "count": r["count"], "label": r["label"]}
            for r in quest["requirements"]
        ],
        "reward_reputation": quest["reward_reputation"],
        "patron": {
            "name": patron["name"],
            "display": patron["display"],
            "emoji": patron["emoji"],
            "color": patron["color"],
        } if patron else {"name": quest["patron"], "display": quest["patron"], "emoji": "🧑", "color": "#888"},
        "index": _quest_index,
        "total": len(BUILD_QUESTS),
    }


def complete_current():
    """验收通过：推进到下一任务，返回刚完成的任务概要。"""
    global _quest_index
    done = current_quest()
    _quest_index = (_quest_index + 1) % len(BUILD_QUESTS)
    return {"completed": done["title"], "emoji": done["emoji"],
            "reward_reputation": done["reward_reputation"], "next": current_quest()}
