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

颜色(17种):
brick_red,brick_blue,brick_yellow,brick_green,brick_white,brick_black,brick_orange,brick_purple,brick_pink,brick_cyan,brick_gray,brick_glow,stone,wood,glass,leaves,tree

配色策略:
- 基调: brick_gray/stone (墙壁) + brick_white (边框)
- 强调: brick_gold→brick_yellow (屋顶/装饰) + brick_cyan (窗户/细节)
- 点缀: brick_glow (灯笼/灯光) brick_red (柱子/门框)
- 屋顶: brick_orange/red + dome/cone/pyramid
- 地面: brick_white/brick_cyan 交替(棋盘地板用多条floor)

结构策略:
- 每层2-3格高，颜色交替(如:层1 gray, 层2 white, 层3 gray)
- 四角放 cyl 塔楼(高2倍)，顶部 cone + sphere(glow)
- 屋顶用 dome 或 pyramid，比主体宽1格
- 门窗用 arch + glass，左右对称
- 屋檐用 cornice 包围每层
- 地板用 2色交替的 floor
- 围墙用 wall + fence 城垛
- 灯光: 每个门口、塔顶、屋檐放 brick_glow

坐标: x,z ∈ [-20,20], y ∈ [1,50]
命令: 最多 80 条，追求极致细节
只输出 JSON

示例 - 精美小塔楼:
{"cmds":["floor -6,-6,6,6,1,brick_white","floor -6,-6,6,6,1,brick_cyan","solid -3,1,-3,3,2,3,brick_gray","box -3,3,-3,3,5,3,brick_white","cornice -4,-4,4,4,5,brick_orange","solid -3,6,-3,3,6,3,brick_gray","box -3,7,-3,3,8,3,brick_white","arch 0,1,-3,2,3,glass","arch 0,1,3,2,3,glass","cyl -3,1,-3,1,8,brick_red","cyl 3,1,3,1,8,brick_red","cyl -3,1,-3,1,8,brick_red","cyl 3,1,-3,1,8,brick_red","cone -3,9,-3,2,4,brick_yellow","cone 3,9,3,2,4,brick_yellow","cone -3,9,-3,2,4,brick_yellow","cone 3,9,-3,2,4,brick_yellow","dome 0,9,0,4,brick_orange","sphere 0,13,0,2,brick_glow","sphere -3,13,-3,1,brick_glow","sphere 3,13,3,1,brick_glow","sphere -3,13,3,1,brick_glow","sphere 3,13,-3,1,brick_glow","vline 0,6,8,0,brick_glow","vline 0,3,5,3,brick_glow","vline 0,3,5,-3,brick_glow","ring 0,14,0,5,1,brick_pink","fence -6,-6,6,-6,1,brick_gray","fence -6,6,6,6,1,brick_gray","fence -6,-6,-6,6,1,brick_gray","fence 6,-6,6,6,1,brick_gray"]}"""

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

def call_llm(api_key, base_url, model, user_input):
    """调用 LLM API 生成建筑方块列表 (使用 subprocess curl 避免超时)"""
    import subprocess
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": LLM_SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ],
        "temperature": 0.7,
        "max_tokens": 4096,
        "stream": False,
    }

    payload_str = json.dumps(payload, ensure_ascii=False)
    curl_cmd = [
        "curl", "-s", "-X", "POST", url,
        "-H", "Content-Type: application/json",
        "-H", f"Authorization: Bearer {api_key}",
        "-d", payload_str,
        "--connect-timeout", "10",
        "--max-time", "180",
    ]

    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=200)
        if result.returncode != 0:
            raise Exception(f"curl 错误: {result.stderr[:200]}")
        resp = json.loads(result.stdout)
        if "error" in resp:
            err = resp["error"]
            raise Exception(f"API 错误: {err.get('message', str(err))[:200]}")
        content = resp["choices"][0]["message"]["content"]
        return content
    except subprocess.TimeoutExpired:
        raise Exception("API 调用超时 (200秒)，请尝试更简单的描述或换更快的模型")
    except json.JSONDecodeError:
        raise Exception(f"API 返回非 JSON: {result.stdout[:200]}")
    except Exception as e:
        raise Exception(str(e))

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
    except:
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
                    except:
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
        except:
            pass

    # 尝试提取 ``` 块
    code_block = re.search(r'```\s*(\{.*?\})\s*```', content, re.DOTALL)
    if code_block:
        try:
            data = json.loads(code_block.group(1))
            if "cmds" in data:
                return data["cmds"]
        except:
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
                    except:
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
