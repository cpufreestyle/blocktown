"""Luanti Builder - llm 模块。"""
import json
import math
import re
import urllib.request
import urllib.error

# ============================================================
# LLM 大模型生成
# ============================================================

LLM_SYSTEM_PROMPT = """你是世界顶级建筑大师，精通 voxel 建筑设计。生成极致精美的建筑。
核心原则: 对称、层次、对比、细节、光影。

命令:
{"cmds":[...]}

形状命令:
- box x1,y1,z1,x2,y2,z2,type: 空心长方体(6面外壳)
- solid x1,y1,z1,x2,y2,z2,type: 实心
- cyl x,y,z,r,h,type: 圆柱
- cone x,y,z,r,h,type: 圆锥
- sphere x,y,z,r,type: 球壳
- dome x,y,z,r,type: 穹顶
- ring x,y,z,r,th,type: 圆环
- pyramid x,y,z,s,type: 金字塔壳
- arch x,y,z,w,h,type: 拱门
- stairs x1,y1,z1,x2,y2,z2,type: 阶梯
- spiral x,y,z,r,h,type: 螺旋
- line x1,y1,z1,x2,y2,z2,type: 线
- hline x,y,z1,z2,type: 水平线
- vline x,y1,y2,z,type: 垂直线
- floor x1,z1,x2,z2,y,type: 地板
- wall x1,y1,z1,x2,y2,z2,type: 薄墙
- cross x,y,z,s,type: 十字
- taper x,y,z,r1,r2,h,type: 圆台(上细下粗)
- fence x1,z1,x2,z2,y,type: 围栏(间隔柱)
- cornice x1,z1,x2,z2,y,type: 屋檐(边缘突出1格)
- roof x1,z1,x2,z2,y0,height,type: 人字形屋顶(三角截面)
- window x,y,z,w,h,type: 窗框(空心矩形)
- column x,y,z,h,type: 装饰柱(带柱头柱础)
- beam x1,y1,z1,x2,z2,type: 横梁(水平条)
- flag x,y,z,height,type: 旗杆+旗面
- gate x,y,z,w,h,type: 大门(双开门效果)
- balcony x,y,z,w,d,type: 阳台(带栏杆)

颜色(17种):
brick_red,brick_blue,brick_yellow,brick_green,brick_white,brick_black,brick_orange,brick_purple,brick_pink,brick_cyan,brick_gray,brick_glow,stone,wood,glass,leaves,tree

配色策略:
- 基调: brick_gray/stone (墙壁) + brick_white (边框)
- 强调: brick_yellow (屋顶/装饰) + brick_cyan (窗户/细节)
- 点缀: brick_glow (灯笼/灯光) brick_red (柱子/门框)
- 屋顶: brick_orange/red + dome/cone/pyramid/roof
- 地面: brick_white/brick_cyan 交替(棋盘地板用多条floor)

结构策略:
- 每层2-3格高，颜色交替(如:层1 gray, 层2 white, 层3 gray)
- 四角放 cyl 或 column 塔楼(高2倍)，顶部 cone + sphere(glow)
- 屋顶用 dome/pyramid/roof，比主体宽1格
- 门窗用 arch + glass 或 window，左右对称
- 屋檐用 cornice 包围每层
- 地板用 2色交替的 floor
- 围墙用 wall + fence 城垛
- 灯光: 每个门口、塔顶、屋檐放 brick_glow
- 用 column 替代 cyl 做更有细节的柱子
- 用 roof 做人字形屋顶增加变化
- 用 balcony 增加层次感

坐标: x,z ∈ [-20,20], y ∈ [1,50]
命令: 最多 120 条，追求极致细节
关键规则:
- 所有坐标必须是整数
- 建筑必须关于 x 轴和 z 轴对称
- 层高 2-3 格，屋顶比主体宽 1-2 格
- 只输出纯 JSON，前后不要 ``` 标记或任何解释文字

示例 - 精美宫殿:
{"cmds":["floor -8,-8,8,8,1,brick_white","floor -8,-8,8,8,1,brick_cyan","solid -5,1,-5,5,3,5,brick_gray","box -5,4,-5,5,7,5,brick_white","cornice -6,-6,6,6,7,brick_orange","solid -5,8,-5,5,8,5,brick_gray","box -5,9,-5,5,11,5,brick_white","roof -6,-6,6,6,12,4,brick_red","column -5,1,-5,9,brick_red","column 5,1,5,9,brick_red","column -5,1,5,9,brick_red","column 5,1,-5,9,brick_red","arch 0,1,-5,3,4,glass","arch 0,1,5,3,4,glass","window -3,4,-5,2,3,glass","window 3,4,-5,2,3,glass","window -3,4,5,2,3,glass","window 3,4,5,2,3,glass","balcony 0,8,5,4,2,brick_white","dome 0,12,0,5,brick_orange","sphere 0,17,0,2,brick_glow","cone -5,12,-5,2,4,brick_yellow","cone 5,12,5,2,4,brick_yellow","cone -5,12,5,2,4,brick_yellow","cone 5,12,-5,2,4,brick_yellow","flag 0,17,0,3,brick_glow","vline 0,4,8,0,brick_glow","beam -5,8,-5,5,brick_yellow","beam -5,8,5,5,brick_yellow","ring 0,18,0,6,1,brick_pink","fence -8,-8,8,-8,1,brick_gray","fence -8,8,8,8,1,brick_gray","fence -8,-8,-8,8,1,brick_gray","fence 8,-8,8,8,1,brick_gray"]}"""

# 简单缓存: 相同输入+模型不重复调用
_LLM_CACHE = {}
def _cache_key(api_key, base_url, model, user_input):
    return f"{api_key[:8]}|{model}|{user_input}"

def get_cached(key):
    return _LLM_CACHE.get(key)

def set_cached(key, value):
    if len(_LLM_CACHE) > 20:
        _LLM_CACHE.clear()
    _LLM_CACHE[key] = value

BLOCK_TYPE_TO_LUA = {
    "brick_red": "my_first_mod:brick_red",
    "brick_blue": "my_first_mod:brick_blue",
    "brick_yellow": "my_first_mod:brick_yellow",
    "brick_green": "my_first_mod:brick_green",
    "brick_white": "my_first_mod:brick_white",
    "brick_black": "my_first_mod:brick_black",
    "brick_orange": "my_first_mod:brick_orange",
    "brick_purple": "my_first_mod:brick_purple",
    "brick_pink": "my_first_mod:brick_pink",
    "brick_cyan": "my_first_mod:brick_cyan",
    "brick_gray": "my_first_mod:brick_gray",
    "brick_glow": "my_first_mod:brick_glow",
    "stone": "default:stone",
    "wood": "default:wood",
    "glass": "default:glass",
    "dirt": "default:dirt",
    "sand": "default:sandstone",
    "leaves": "default:leaves",
    "tree": "default:tree",
    "water": "default:water_source",
}

BLOCK_TYPE_TO_COLOR = {
    "brick_red": "#e74c3c", "brick_blue": "#3498db", "brick_yellow": "#f1c40f",
    "brick_green": "#2ecc71", "brick_white": "#ecf0f1", "brick_black": "#2c3e50",
    "brick_orange": "#e67e22", "brick_purple": "#9b59b6", "brick_pink": "#fd79a8",
    "brick_cyan": "#00cec9", "brick_gray": "#95a5a6", "brick_glow": "#ffeaa7",
    "stone": "#7f8c8d", "wood": "#8b6914", "glass": "#74b9ff",
    "dirt": "#6b4226", "sand": "#f5deb3", "leaves": "#27ae60",
    "tree": "#5d4037", "water": "#2980b9",
}

def _post_chat(model, api_key, base_url, messages, max_tokens=4096, temperature=0.7):
    """公共 LLM 请求: subprocess curl + 超时/网络错误重试一次; API 错误直接抛出"""
    import subprocess
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {"model": model, "messages": messages,
               "temperature": temperature, "max_tokens": max_tokens, "stream": False}
    payload_str = json.dumps(payload, ensure_ascii=False)
    curl_cmd = [
        "curl", "-s", "-X", "POST", url,
        "-H", "Content-Type: application/json",
        "-H", f"Authorization: Bearer {api_key}",
        "-d", payload_str,
        "--connect-timeout", "10",
        "--max-time", "180",
    ]
    last_err = None
    for attempt in range(2):
        try:
            result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=200)
            if result.returncode != 0:
                raise ConnectionError(f"curl 错误: {result.stderr[:200]}")
            resp = json.loads(result.stdout)
            if "error" in resp:
                err = resp["error"]
                raise RuntimeError(f"API 错误: {err.get('message', str(err))[:200]}")
            return resp["choices"][0]["message"]["content"]
        except subprocess.TimeoutExpired:
            last_err = Exception("API 调用超时 (200秒)，请尝试更简单的描述或换更快的模型")
        except (ConnectionError, json.JSONDecodeError) as e:
            last_err = Exception(f"网络/响应错误: {e}")
        except RuntimeError:
            raise  # API 错误直接抛出
    raise last_err

def call_llm(api_key, base_url, model, user_input):
    """调用 LLM API 生成建筑方块列表 (缓存 + curl)"""
    # 缓存检查
    ck = _cache_key(api_key, base_url, model, user_input)
    cached = get_cached(ck)
    if cached:
        return cached
    messages = [
        {"role": "system", "content": LLM_SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]
    content = _post_chat(model, api_key, base_url, messages)
    set_cached(ck, content)
    return content

CHAT_ITERATE_RULES = """

迭代修改模式:
- 用户消息是对当前建筑的修改要求 (如"把屋顶改成金色"、"再加两层塔楼")
- 你必须在当前建筑基础上增量修改，保留未被要求改动的部分
- 输出修改后的完整 cmds 列表 (不是只输出差异)
- 同样只输出纯 JSON"""

MAX_HISTORY_TURNS = 8

def call_llm_chat(api_key, base_url, model, user_input, history=None, current_cmds=None):
    """对话式迭代建造: 基于历史对话与当前建筑 cmds 增量修改"""
    messages = [{"role": "system", "content": LLM_SYSTEM_PROMPT + CHAT_ITERATE_RULES}]
    if current_cmds:
        cmds_preview = json.dumps(list(current_cmds)[:120], ensure_ascii=False)
        messages.append({"role": "system", "content": f"当前建筑的完整 cmds 列表:\n{{\"cmds\":{cmds_preview}}}"})
    if history:
        for h in history[-MAX_HISTORY_TURNS*2:]:
            role = h.get("role", "user")
            if role in ("user", "assistant") and h.get("content"):
                messages.append({"role": role, "content": str(h["content"])[:1000]})
    messages.append({"role": "user", "content": user_input})

    hist_key = json.dumps(messages, ensure_ascii=False, sort_keys=True)
    ck = _cache_key(api_key, base_url, model, hist_key[:500])
    cached = get_cached(ck)
    if cached:
        return cached

    content = _post_chat(model, api_key, base_url, messages)
    set_cached(ck, content)
    return content

REFINE_SYSTEM_PROMPT = """你是世界顶级建筑评审 + 建筑大师。审视给定的 voxel 建筑 cmds，从以下维度找问题并改进:
1. 对称性 (建筑应关于 x/z 轴对称)
2. 层次感 (每层 2-3 格高、颜色交替、屋顶比主体宽 1-2 格)
3. 色彩 (基调 gray/stone + 白色边框 + 黄/橙屋顶 + glow 灯光点缀)
4. 细节 (窗户/柱子/屋檐/旗帜/灯笼是否充分)
5. 轮廓 (顶部是否单调，需要 dome/cone/roof 变化)
只输出改进后的完整 cmds JSON ({"cmds":[...]})，格式与输入一致。保持原建筑识别度，只做优化。

形状命令与颜色规格同前: box/solid/cyl/cone/sphere/dome/ring/pyramid/arch/stairs/spiral/line/hline/vline/floor/wall/cross/taper/fence/cornice/roof/window/column/beam/flag/gate/balcony; 17色 brick_*。坐标 x,z∈[-20,20], y∈[1,50], 整数, ≤120 条命令。只输出纯 JSON。"""

def call_llm_refine(api_key, base_url, model, user_input, cmds, image_data_url=None):
    """AI 审美迭代: 审视当前建筑 (可选附预览截图) 并输出改进后的 cmds

    带图片请求失败时自动降级为纯文本批评 (无视觉模型场景)。
    Returns: (new_cmds, note)  note 描述是否使用了视觉
    """
    cmds_preview = json.dumps(list(cmds)[:120], ensure_ascii=False)
    text = (f"原始需求: {user_input}\n\n当前建筑的 cmds:\n{{\"cmds\":{cmds_preview}}}\n\n"
            "请评审并输出改进后的完整 cmds JSON。")

    if image_data_url:
        messages = [
            {"role": "system", "content": REFINE_SYSTEM_PROMPT},
            {"role": "user", "content": [
                {"type": "text", "text": text + "\n附图为该建筑的 3D 预览截图，请结合视觉观感评审。"},
                {"type": "image_url", "image_url": {"url": image_data_url}},
            ]},
        ]
        try:
            content = _post_chat(model, api_key, base_url, messages, temperature=0.6)
            new_cmds = parse_llm_json(content)
            if new_cmds:
                return (new_cmds if isinstance(new_cmds, list) else new_cmds.get("cmds", []), "vision")
        except RuntimeError:
            pass  # 视觉不支持/图片过大 → 降级纯文本

    messages = [
        {"role": "system", "content": REFINE_SYSTEM_PROMPT},
        {"role": "user", "content": text},
    ]
    content = _post_chat(model, api_key, base_url, messages, temperature=0.6)
    new_cmds = parse_llm_json(content)
    if not new_cmds:
        raise ValueError("AI 返回无法解析为 cmds")
    return (new_cmds if isinstance(new_cmds, list) else new_cmds.get("cmds", []), "text")

def parse_llm_json(content):
    """从 LLM 回复中提取命令列表"""
    # 去除前后空白
    content = content.strip()

    # 尝试直接解析
    try:
        data = json.loads(content)
        if "cmds" in data:
            return data["cmds"]
        if "blocks" in data:
            return data  # 旧格式兼容
    except (ValueError, TypeError):
        pass

    # 尝试提取第一个完整 JSON 对象
    brace_start = content.find('{')
    if brace_start >= 0:
        depth = 0
        for i in range(brace_start, len(content)):
            if content[i] == '{':
                depth += 1
            elif content[i] == '}':
                depth -= 1
                if depth == 0:
                    json_str = content[brace_start:i+1]
                    try:
                        data = json.loads(json_str)
                        if "cmds" in data:
                            return data["cmds"]
                        if "blocks" in data:
                            return data
                    except (ValueError, TypeError):
                        pass
                    break

    # 尝试提取 ```json 块
    json_block = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
    if json_block:
        try:
            data = json.loads(json_block.group(1))
            if "cmds" in data:
                return data["cmds"]
            if "blocks" in data:
                return data
        except (ValueError, TypeError):
            pass

    # 尝试提取 ``` 块
    code_block = re.search(r'```\s*(\{.*?\})\s*```', content, re.DOTALL)
    if code_block:
        try:
            data = json.loads(code_block.group(1))
            if "cmds" in data:
                return data["cmds"]
        except (ValueError, TypeError):
            pass

    # 最后尝试：找任何包含 cmds 的 JSON (用平衡括号匹配)
    brace_start = content.find('{')
    while brace_start >= 0:
        depth = 0
        for i in range(brace_start, len(content)):
            if content[i] == '{':
                depth += 1
            elif content[i] == '}':
                depth -= 1
                if depth == 0:
                    json_str = content[brace_start:i+1]
                    try:
                        data = json.loads(json_str)
                        if "cmds" in data:
                            return data["cmds"]
                        if "blocks" in data:
                            return data
                    except (ValueError, TypeError):
                        pass
                    break
        brace_start = content.find('{', brace_start + 1)

    # 最后最后尝试：从文本中提取 cmds 数组内容
    cmds_match = re.search(r'"cmds"\s*:\s*\[(.*?)\]', content, re.DOTALL)
    if cmds_match:
        cmds_text = cmds_match.group(1)
        # 提取所有引号内的命令字符串
        cmd_strings = re.findall(r'"([^"]+)"', cmds_text)
        if cmd_strings:
            return cmd_strings

    return None

def cmds_to_blocks(cmds):
    """将命令列表转为方块列表"""
    # 限制命令条数，防止超长响应拖慢解析与游戏
    cmds = cmds[:120]
    blocks = []
    for cmd in cmds:
        cmd = cmd.strip()
        # 分离命令类型和参数
        space_idx = cmd.find(' ')
        if space_idx < 0:
            continue
        cmd_type = cmd[:space_idx]
        rest = cmd[space_idx+1:].strip()

        # 提取方块类型 (最后一个逗号后的单词，或空格后的单词)
        btype = "stone"
        # 尝试: "x1,y1,z1,x2,y2,z2,type" 格式
        last_comma = rest.rfind(',')
        if last_comma >= 0:
            after_comma = rest[last_comma+1:].strip()
            if after_comma and not after_comma.lstrip('-').isdigit():
                btype = after_comma
                rest = rest[:last_comma]
        # 也尝试: "coords type" 格式
        parts2 = rest.rsplit(' ', 1)
        if len(parts2) == 2 and parts2[1] and not parts2[1].lstrip('-').isdigit():
            btype = parts2[1]
            rest = parts2[0]

        coords = [c.strip() for c in rest.split(',')]
        try:
            if cmd_type == "box":
                x1,y1,z1,x2,y2,z2 = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3]),int(coords[4]),int(coords[5])
                for x in range(min(x1,x2), max(x1,x2)+1):
                    for y in range(max(1,min(y1,y2)), max(y1,y2)+1):
                        for z in range(min(z1,z2), max(z1,z2)+1):
                            if x==x1 or x==x2 or y==y1 or y==y2 or z==z1 or z==z2:
                                blocks.append({"x":x,"y":y,"z":z,"type":btype})
            elif cmd_type == "solid":
                x1,y1,z1,x2,y2,z2 = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3]),int(coords[4]),int(coords[5])
                for x in range(min(x1,x2), max(x1,x2)+1):
                    for y in range(max(1,min(y1,y2)), max(y1,y2)+1):
                        for z in range(min(z1,z2), max(z1,z2)+1):
                            blocks.append({"x":x,"y":y,"z":z,"type":btype})
            elif cmd_type == "cyl":
                cx,cy,cz,r,h = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3]),int(coords[4])
                for y in range(max(1,cy), cy+h):
                    for x in range(-r, r+1):
                        for z in range(-r, r+1):
                            if x*x+z*z <= r*r:
                                blocks.append({"x":cx+x,"y":y,"z":cz+z,"type":btype})
            elif cmd_type == "sphere":
                cx,cy,cz,r = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3])
                for x in range(-r, r+1):
                    for y in range(-r, r+1):
                        for z in range(-r, r+1):
                            d = x*x+y*y+z*z
                            if d <= r*r and d >= (r-1)*(r-1):
                                blocks.append({"x":cx+x,"y":max(1,cy+y),"z":cz+z,"type":btype})
            elif cmd_type == "line":
                x1,y1,z1,x2,y2,z2 = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3]),int(coords[4]),int(coords[5])
                steps = max(abs(x2-x1), abs(y2-y1), abs(z2-z1), 1)
                for i in range(steps+1):
                    t = i / steps
                    x = round(x1 + (x2-x1)*t)
                    y = max(1, round(y1 + (y2-y1)*t))
                    z = round(z1 + (z2-z1)*t)
                    blocks.append({"x":x,"y":y,"z":z,"type":btype})
            elif cmd_type == "dome":
                cx,cy,cz,r = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3])
                for x in range(-r, r+1):
                    for y in range(0, r+1):
                        for z in range(-r, r+1):
                            d = x*x + y*y + z*z
                            if d <= r*r and d >= (r-1)*(r-1) and y >= 0:
                                blocks.append({"x":cx+x,"y":max(1,cy+y),"z":cz+z,"type":btype})
            elif cmd_type == "ring":
                cx,cy,cz,r,th = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3]),int(coords[4])
                for x in range(-r-th, r+th+1):
                    for z in range(-r-th, r+th+1):
                        d = math.sqrt(x*x + z*z)
                        if r-th <= d <= r+th:
                            blocks.append({"x":cx+x,"y":max(1,cy),"z":cz+z,"type":btype})
            elif cmd_type == "stairs":
                x1,y1,z1,x2,y2,z2 = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3]),int(coords[4]),int(coords[5])
                dx = 1 if x2 >= x1 else -1
                dy = 1 if y2 >= y1 else -1
                dz = 1 if z2 >= z1 else -1
                steps_x = abs(x2 - x1) + 1
                steps_y = abs(y2 - y1) + 1
                max_steps = max(steps_x, steps_y)
                for i in range(max_steps):
                    x = x1 + dx * min(i, steps_x - 1)
                    y = y1 + dy * min(i, steps_y - 1)
                    z = z1 + dz * min(i, abs(z2 - z1))
                    for zz in range(min(z, z2), max(z, z2) + 1):
                        blocks.append({"x":x,"y":max(1,y),"z":zz,"type":btype})
            elif cmd_type == "arch":
                cx,cy,cz,w,h = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3]),int(coords[4])
                r = max(w, h)
                for x in range(-w, w+1):
                    for y in range(0, h+1):
                        d = math.sqrt(x*x + (h - y)*(h - y))
                        if abs(d - r) <= 1 and y < h:
                            blocks.append({"x":cx+x,"y":max(1,cy+y),"z":cz,"type":btype})
                        elif y == 0 and abs(x) <= w:
                            blocks.append({"x":cx+x,"y":max(1,cy),"z":cz,"type":btype})
            elif cmd_type == "cone":
                cx,cy,cz,r,h = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3]),int(coords[4])
                for y in range(h):
                    layer_r = max(0, r - int(y * r / h))
                    for x in range(-layer_r, layer_r+1):
                        for z in range(-layer_r, layer_r+1):
                            if x*x+z*z <= layer_r*layer_r:
                                blocks.append({"x":cx+x,"y":max(1,cy+y),"z":cz+z,"type":btype})
            elif cmd_type == "pyramid":
                cx,cy,cz,sz = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3])
                for y in range(sz+1):
                    r = sz - y
                    for x in range(-r, r+1):
                        for z in range(-r, r+1):
                            if x == -r or x == r or z == -r or z == r or y == sz:
                                blocks.append({"x":cx+x,"y":max(1,cy+y),"z":cz+z,"type":btype})
            elif cmd_type == "cross":
                cx,cy,cz,sz = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3])
                for i in range(-sz, sz+1):
                    blocks.append({"x":cx+i,"y":max(1,cy),"z":cz,"type":btype})
                    blocks.append({"x":cx,"y":max(1,cy+i),"z":cz,"type":btype})
                    blocks.append({"x":cx,"y":max(1,cy),"z":cz+i,"type":btype})
            elif cmd_type == "spiral":
                cx,cy,cz,r,h = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3]),int(coords[4])
                for y in range(h):
                    angle = y * 0.8
                    x = round(math.cos(angle) * r)
                    z = round(math.sin(angle) * r)
                    blocks.append({"x":cx+x,"y":max(1,cy+y),"z":cz+z,"type":btype})
            elif cmd_type == "wall":
                x1,y1,z1,x2,y2,z2 = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3]),int(coords[4]),int(coords[5])
                for x in range(min(x1,x2), max(x1,x2)+1):
                    for y in range(max(1,min(y1,y2)), max(y1,y2)+1):
                        for z in range(min(z1,z2), max(z1,z2)+1):
                            if abs(x-x1) + abs(z-z1) <= 1 or abs(x-x2) + abs(z-z2) <= 1:
                                pass  # skip corners for thin wall
                            if (z1 == z2 and z == z1) or (x1 == x2 and x == x1):
                                blocks.append({"x":x,"y":y,"z":z,"type":btype})
                # Also handle diagonal walls
                if x1 != x2 and z1 != z2:
                    steps = max(abs(x2-x1), abs(z2-z1), 1)
                    for i in range(steps+1):
                        t = i / steps
                        x = round(x1 + (x2-x1)*t)
                        y = max(1, min(y1, y2))
                        z = round(z1 + (z2-z1)*t)
                        for yy in range(max(1,min(y1,y2)), max(y1,y2)+1):
                            blocks.append({"x":x,"y":yy,"z":z,"type":btype})
            elif cmd_type == "floor":
                x1,z1,x2,z2,y = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3]),int(coords[4])
                for x in range(min(x1,x2), max(x1,x2)+1):
                    for z in range(min(z1,z2), max(z1,z2)+1):
                        blocks.append({"x":x,"y":max(1,y),"z":z,"type":btype})
            elif cmd_type == "hline":
                x,y,z1,z2 = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3])
                for z in range(min(z1,z2), max(z1,z2)+1):
                    blocks.append({"x":x,"y":max(1,y),"z":z,"type":btype})
            elif cmd_type == "vline":
                x,y1,y2,z = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3])
                for y in range(max(1,min(y1,y2)), max(y1,y2)+1):
                    blocks.append({"x":x,"y":y,"z":z,"type":btype})
            elif cmd_type == "taper":
                cx,cy,cz,r1,r2,h = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3]),int(coords[4]),int(coords[5])
                for y in range(h):
                    t = y / max(h-1, 1)
                    r = round(r1 + (r2 - r1) * t)
                    for x in range(-r, r+1):
                        for z in range(-r, r+1):
                            d = math.sqrt(x*x + z*z)
                            if d <= r and d >= r - 1:
                                blocks.append({"x":cx+x,"y":max(1,cy+y),"z":cz+z,"type":btype})
            elif cmd_type == "fence":
                x1,z1,x2,z2,y = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3]),int(coords[4])
                for x in range(min(x1,x2), max(x1,x2)+1, 2):
                    blocks.append({"x":x,"y":max(1,y),"z":z1,"type":btype})
                    blocks.append({"x":x,"y":max(1,y+1),"z":z1,"type":btype})
                for z in range(min(z1,z2), max(z1,z2)+1, 2):
                    blocks.append({"x":x1,"y":max(1,y),"z":z,"type":btype})
                    blocks.append({"x":x1,"y":max(1,y+1),"z":z,"type":btype})
            elif cmd_type == "cornice":
                x1,z1,x2,z2,y = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3]),int(coords[4])
                for x in range(min(x1,x2), max(x1,x2)+1):
                    blocks.append({"x":x,"y":max(1,y),"z":z1-1,"type":btype})
                    blocks.append({"x":x,"y":max(1,y),"z":z2+1,"type":btype})
                    blocks.append({"x":x,"y":max(1,y+1),"z":z1-1,"type":btype})
                    blocks.append({"x":x,"y":max(1,y+1),"z":z2+1,"type":btype})
                for z in range(min(z1,z2), max(z1,z2)+1):
                    blocks.append({"x":x1-1,"y":max(1,y),"z":z,"type":btype})
                    blocks.append({"x":x2+1,"y":max(1,y),"z":z,"type":btype})
                    blocks.append({"x":x1-1,"y":max(1,y+1),"z":z,"type":btype})
                    blocks.append({"x":x2+1,"y":max(1,y+1),"z":z,"type":btype})
            elif cmd_type == "roof":
                # 人字形屋顶: x1,z1,x2,z2,y0,height,type
                x1,z1,x2,z2,y0,h = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3]),int(coords[4]),int(coords[5])
                half_w = (max(x1,x2) - min(x1,x2)) // 2
                mid_x = (x1 + x2) // 2
                for y in range(h):
                    offset = int(y * half_w / max(h, 1))
                    lx = mid_x - offset
                    rx = mid_x + offset
                    for z in range(min(z1,z2), max(z1,z2)+1):
                        blocks.append({"x":lx,"y":max(1,y0+y),"z":z,"type":btype})
                        if lx != rx:
                            blocks.append({"x":rx,"y":max(1,y0+y),"z":z,"type":btype})
                        # 填充屋顶中间
                        for xx in range(lx+1, rx):
                            blocks.append({"x":xx,"y":max(1,y0+y),"z":z,"type":btype})
            elif cmd_type == "window":
                # 窗框: x,y,z,w,h,type (空心矩形)
                wx,wy,wz,w,h = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3]),int(coords[4])
                for dx in range(-w, w+1):
                    blocks.append({"x":wx+dx,"y":max(1,wy),"z":wz,"type":btype})
                    blocks.append({"x":wx+dx,"y":max(1,wy+h),"z":wz,"type":btype})
                for dy in range(0, h+1):
                    blocks.append({"x":wx-w,"y":max(1,wy+dy),"z":wz,"type":btype})
                    blocks.append({"x":wx+w,"y":max(1,wy+dy),"z":wz,"type":btype})
            elif cmd_type == "column":
                # 装饰柱(带柱头柱础): x,y,z,h,type
                cx,cy,cz,h = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3])
                for y in range(h):
                    blocks.append({"x":cx,"y":max(1,cy+y),"z":cz,"type":btype})
                # 柱头(宽2格十字)
                blocks.append({"x":cx+1,"y":max(1,cy),"z":cz,"type":btype})
                blocks.append({"x":cx-1,"y":max(1,cy),"z":cz,"type":btype})
                blocks.append({"x":cx,"y":max(1,cy),"z":cz+1,"type":btype})
                blocks.append({"x":cx,"y":max(1,cy),"z":cz-1,"type":btype})
                blocks.append({"x":cx+1,"y":max(1,cy+h-1),"z":cz,"type":btype})
                blocks.append({"x":cx-1,"y":max(1,cy+h-1),"z":cz,"type":btype})
                blocks.append({"x":cx,"y":max(1,cy+h-1),"z":cz+1,"type":btype})
                blocks.append({"x":cx,"y":max(1,cy+h-1),"z":cz-1,"type":btype})
            elif cmd_type == "beam":
                # 横梁: x1,y1,z1,x2,z2,type
                x1,y1,z1,x2,z2 = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3]),int(coords[4])
                for z in range(min(z1,z2), max(z1,z2)+1):
                    blocks.append({"x":x1,"y":max(1,y1),"z":z,"type":btype})
                    if x1 != x2:
                        blocks.append({"x":x2,"y":max(1,y1),"z":z,"type":btype})
            elif cmd_type == "flag":
                # 旗杆+旗面: x,y,z,height,type
                fx,fy,fz,h = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3])
                for y in range(h):
                    blocks.append({"x":fx,"y":max(1,fy+y),"z":fz,"type":"wood"})
                # 旗面(旗杆顶部向一侧延伸)
                for dx in range(1, 4):
                    blocks.append({"x":fx+dx,"y":max(1,fy+h-1),"z":fz,"type":btype})
                    blocks.append({"x":fx+dx,"y":max(1,fy+h-2),"z":fz,"type":btype})
            elif cmd_type == "gate":
                # 大门: x,y,z,w,h,type (双开门效果)
                gx,gy,gz,w,h = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3]),int(coords[4])
                # 门框
                for dx in range(-w-1, w+2):
                    blocks.append({"x":gx+dx,"y":max(1,gy),"z":gz,"type":btype})
                    blocks.append({"x":gx+dx,"y":max(1,gy+h),"z":gz,"type":btype})
                for dy in range(0, h+1):
                    blocks.append({"x":gx-w-1,"y":max(1,gy+dy),"z":gz,"type":btype})
                    blocks.append({"x":gx+w+1,"y":max(1,gy+dy),"z":gz,"type":btype})
                # 中线分隔
                for dy in range(1, h):
                    blocks.append({"x":gx,"y":max(1,gy+dy),"z":gz,"type":btype})
            elif cmd_type == "balcony":
                # 阳台: x,y,z,w,d,type
                bx,by,bz,w,d = int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3]),int(coords[4])
                # 地板
                for dx in range(-w, w+1):
                    for dz in range(0, d+1):
                        blocks.append({"x":bx+dx,"y":max(1,by),"z":bz+dz,"type":btype})
                # 栏杆
                for dx in range(-w, w+1, 2):
                    blocks.append({"x":bx+dx,"y":max(1,by+1),"z":bz+d,"type":btype})
                    blocks.append({"x":bx+dx,"y":max(1,by+2),"z":bz+d,"type":btype})
                for dz in range(0, d+1, 2):
                    blocks.append({"x":bx-w,"y":max(1,by+1),"z":bz+cz,"type":btype})
                    blocks.append({"x":bx+w,"y":max(1,by+1),"z":bz+cz,"type":btype})
        except (ValueError, IndexError):
            continue
    # 限制总数
    if len(blocks) > 2000:
        step = len(blocks) // 2000
        blocks = blocks[::step][:2000]
    return blocks

def blocks_to_lua(blocks, user_input):
    """将方块列表转为 Lua mod 代码"""
    lua_blocks = []
    valid_blocks = []
    for b in blocks:
        x = b.get("x", 0)
        y = max(1, b.get("y", 1))
        z = b.get("z", 0)
        btype = b.get("type", "stone")
        lua_name = BLOCK_TYPE_TO_LUA.get(btype, "default:stone")
        color = BLOCK_TYPE_TO_COLOR.get(btype, "#7f8c8d")
        valid_blocks.append({"x": x, "y": y, "z": z, "type": btype, "color": color})
        lua_blocks.append(f'minetest.set_node({{x=pos.x+{x}, y=pos.y+{y}, z=pos.z+{z}}}, {{name="{lua_name}"}})')

    lua = f'''-- nl_builder mod - AI 生成
-- 输入: {user_input}
-- 方块数: {len(valid_blocks)}

local function build_structure(pos)
    -- 填平地面
    local r = 30
    for x = -r, r do for z = -r, r do
        local n = minetest.get_node_or_nil({{x=pos.x+x, y=pos.y, z=pos.z+z}})
        if n and (n.name == "air" or n.name == "default:water_source" or n.name == "default:water_flowing") then
            minetest.set_node({{x=pos.x+x, y=pos.y, z=pos.z+z}}, {{name="default:stone"}})
        end
    end end
    -- 清除上方
    for x = -r, r do for y = 1, r+50 do for z = -r, r do
        minetest.set_node({{x=pos.x+x, y=pos.y+y, z=pos.z+z}}, {{name="air"}})
    end end end
    -- 放置方块
    {chr(10).join(lua_blocks[:1500])}
end

minetest.register_chatcommand("build", {{
    description = "生成AI建筑",
    func = function(name, param)
        local player = minetest.get_player_by_name(name)
        if not player then return false, "玩家不存在" end
        local pos = player:get_pos()
        pos.y = math.floor(pos.y)
        for dy = -3, 3 do
            local node = minetest.get_node_or_nil({{x=pos.x, y=pos.y+dy, z=pos.z}})
            local def = node and minetest.registered_nodes[node.name]
            if def and def.walkable and node.name ~= "air" then
                pos.y = pos.y + dy
                break
            end
        end
        -- 建筑生成在玩家前方15格，避免罩住玩家
        local dir = player:get_look_dir()
        pos.x = pos.x + math.floor(dir.x * 15)
        pos.z = pos.z + math.floor(dir.z * 15)
        pos.y = math.floor(pos.y)
        for dy = -5, 5 do
            local node = minetest.get_node_or_nil({{x=pos.x, y=pos.y+dy, z=pos.z}})
            local def = node and minetest.registered_nodes[node.name]
            if def and def.walkable and node.name ~= "air" then
                pos.y = pos.y + dy
                break
            end
        end
        build_structure(pos)
        return true, "AI建筑已生成！({len(valid_blocks)} 个方块)"
    end,
}})

print("[nl_builder] AI建筑 mod 加载完成")
'''
    return lua, valid_blocks
