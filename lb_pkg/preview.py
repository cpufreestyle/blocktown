"""Luanti Builder - preview 模块。"""

# ============================================================
# 预览方块生成
# ============================================================

COLOR_HEX = {
    "red":"#e74c3c","blue":"#3498db","yellow":"#f1c40f","green":"#2ecc71",
    "white":"#ecf0f1","black":"#2c3e50","orange":"#e67e22","purple":"#9b59b6",
    "pink":"#fd79a8","cyan":"#00cec9","gray":"#95a5a6","lime":"#a4c400",
    "wood":"#8b6914","stone":"#7f8c8d","brick":"#c0392b","sand":"#f5deb3",
    "glass":"#74b9ff","iron":"#bdc3c7","dirt":"#6b4226","snow":"#ffffff",
    "water":"#2980b9","leaves":"#27ae60","tree":"#5d4037","grass":"#4a7c3f",
    "glow":"#ffeaa7","fence":"#8b6914","furnace":"#e74c3c",
    "default":"#7f8c8d",
}

def get_color_hex(color_name, material_name=None, block_name=None):
    """获取颜色十六进制值"""
    # 直接匹配 block_name
    if block_name:
        for k, v in COLOR_HEX.items():
            if k in block_name.lower():
                return v
    # 匹配颜色
    if color_name and color_name in COLOR_HEX:
        return COLOR_HEX[color_name]
    # 匹配材质
    if material_name and material_name in COLOR_HEX:
        return COLOR_HEX[material_name]
    return COLOR_HEX["default"]

def gen_preview_blocks(params):
    """生成预览方块列表 [{x,y,z,color}]"""
    btype = params["type"] or "house"
    color = params["color"] or "gray"
    size = params["size"]
    material = params["material"]
    sm = [0.6, 1.0, 1.5, 2.5][size]
    hex_color = get_color_hex(color, material)

    blocks = []
    s = max(1, int(sm * 2))  # 预览缩放为整数

    if btype == "castle":
        h = 8 * s; w = 10 * s
        # 城墙 (仅外壳，采样)
        for x in range(-w, w+1, 2):
            for y in range(0, h+1, 2):
                blocks.append({"x": x, "y": y, "z": -w, "color": hex_color})
                blocks.append({"x": x, "y": y, "z": w, "color": hex_color})
            blocks.append({"x": -w, "y": y, "z": x, "color": hex_color})
            blocks.append({"x": w, "y": y, "z": x, "color": hex_color})
        # 四角塔
        for cx, cz in [(-w,-w),(w,-w),(-w,w),(w,w)]:
            for y in range(0, h + s*4, 2):
                r = s
                for dx in range(-r, r+1, 1):
                    for dz in range(-r, r+1, 1):
                        if dx*dx+dz*dz <= r*r:
                            blocks.append({"x": cx+dx, "y": y, "z": cz+dz, "color": hex_color})
        # 塔顶球
        for cx, cz in [(-w,-w),(w,-w),(-w,w),(w,w)]:
            r = s
            for dx in range(-r, r+1):
                for dy in range(-r, r+1):
                    for dz in range(-r, r+1):
                        if dx*dx+dy*dy+dz*dz <= r*r:
                            blocks.append({"x": cx+dx, "y": h+s*4+dy, "z": cz+dz, "color": hex_color})
    elif btype == "house":
        h = 4 * s; w = 5 * s
        for x in range(-w, w+1, 1):
            blocks.append({"x": x, "y": 0, "z": -w, "color": hex_color})
            blocks.append({"x": x, "y": h, "z": -w, "color": hex_color})
            blocks.append({"x": x, "y": 0, "z": w, "color": hex_color})
            blocks.append({"x": x, "y": h, "z": w, "color": hex_color})
        for z in range(-w, w+1, 1):
            blocks.append({"x": -w, "y": 0, "z": z, "color": hex_color})
            blocks.append({"x": -w, "y": h, "z": z, "color": hex_color})
            blocks.append({"x": w, "y": 0, "z": z, "color": hex_color})
            blocks.append({"x": w, "y": h, "z": z, "color": hex_color})
        # 屋顶
        for x in range(-w-1, w+2, 1):
            for z in range(-w-1, w+2, 1):
                blocks.append({"x": x, "y": h+1, "z": z, "color": COLOR_HEX["wood"]})
    elif btype == "tower":
        h = 20 * s; r = max(2, 3 * s)
        for y in range(0, h, 1):
            for x in range(-r, r+1):
                for z in range(-r, r+1):
                    if x*x+z*z <= r*r:
                        blocks.append({"x": x, "y": y, "z": z, "color": hex_color})
        # 尖顶
        for y in range(h, h + 5*s):
            rr = max(1, r - (y - h))
            for x in range(-rr, rr+1):
                for z in range(-rr, rr+1):
                    if x*x+z*z <= rr*rr:
                        blocks.append({"x": x, "y": y, "z": z, "color": hex_color})
        blocks.append({"x": 0, "y": h + 5*s + 1, "z": 0, "color": COLOR_HEX["glow"]})
    elif btype == "pyramid":
        h = 10 * s
        for y in range(0, h+1):
            r = h - y
            for x in range(-r, r+1, 1):
                for z in range(-r, r+1, 1):
                    if x == -r or x == r or z == -r or z == r or y == 0 or y == h:
                        blocks.append({"x": x, "y": y, "z": z, "color": hex_color})
    elif btype == "sphere":
        r = max(3, 6 * s)
        for x in range(-r, r+1):
            for y in range(-r, r+1):
                for z in range(-r, r+1):
                    d = x*x + y*y + z*z
                    if d <= r*r and d >= (r-1)*(r-1):
                        blocks.append({"x": x, "y": y + r, "z": z, "color": hex_color})
    elif btype == "heart":
        scale = max(1, s)
        pattern = [".##...##.","#########","#########","#########",".#######.","..#####..","...###...","....#...."]
        for row, line in enumerate(pattern):
            for col, ch in enumerate(line):
                if ch == '#':
                    blocks.append({"x": col*scale, "y": (len(pattern)-row)*scale, "z": 0, "color": hex_color})
    elif btype == "tree":
        th = 8 * s; tr = 4 * s
        for y in range(0, th):
            blocks.append({"x": 0, "y": y, "z": 0, "color": COLOR_HEX["tree"]})
        for x in range(-tr, tr+1):
            for y in range(0, tr*2+1):
                for z in range(-tr, tr+1):
                    d = x*x + (y-tr)*(y-tr) + z*z
                    if d <= tr*tr:
                        blocks.append({"x": x, "y": th+y, "z": z, "color": COLOR_HEX["leaves"]})
    elif btype == "fountain":
        r = 4 * s
        for x in range(-r, r+1):
            for z in range(-r, r+1):
                if x*x+z*z <= r*r and x*x+z*z >= (r-1)*(r-1):
                    blocks.append({"x": x, "y": 0, "z": z, "color": hex_color})
        for y in range(0, 3*s):
            blocks.append({"x": 0, "y": y+1, "z": 0, "color": hex_color})
        for x in range(-2, 3):
            for z in range(-2, 3):
                if x*x+z*z <= 4:
                    blocks.append({"x": x, "y": 3*s+2, "z": z, "color": COLOR_HEX["water"]})
    elif btype == "lighthouse":
        h = 15 * s; r = max(2, 3 * s)
        for y in range(0, h):
            c = hex_color if (y // (s*2)) % 2 == 0 else COLOR_HEX["white"]
            for x in range(-r, r+1):
                for z in range(-r, r+1):
                    if x*x+z*z <= r*r and x*x+z*z >= (r-1)*(r-1):
                        blocks.append({"x": x, "y": y, "z": z, "color": c})
        blocks.append({"x": 0, "y": h+2, "z": 0, "color": COLOR_HEX["glow"]})
    elif btype == "bridge":
        length = 20 * s; h = 5 * s
        for x in range(0, length+1, 1):
            for z in range(-3, 4):
                blocks.append({"x": x, "y": h, "z": z, "color": hex_color})
        for y in range(0, h):
            blocks.append({"x": 0, "y": y, "z": 0, "color": hex_color})
            blocks.append({"x": length, "y": y, "z": 0, "color": hex_color})
    elif btype == "mushroom":
        h = 5 * s; r = max(2, 3 * s)
        for y in range(0, h):
            blocks.append({"x": 0, "y": y, "z": 0, "color": COLOR_HEX["white"]})
        for x in range(-r, r+1):
            for y in range(-r, r+1):
                for z in range(-r, r+1):
                    d = x*x + y*y + z*z
                    if d <= r*r and y >= 0:
                        blocks.append({"x": x, "y": h+y, "z": z, "color": hex_color})
    elif btype == "garden":
        w = 8 * s
        for x in range(-w, w+1, 2):
            for z in range(-w, w+1, 2):
                blocks.append({"x": x, "y": 0, "z": z, "color": COLOR_HEX["grass"]})
        # 中心树
        for y in range(0, 4*s):
            blocks.append({"x": 0, "y": y+1, "z": 0, "color": COLOR_HEX["tree"]})
        r = 3 * s
        for x in range(-r, r+1):
            for y in range(-r, r+1):
                for z in range(-r, r+1):
                    if x*x+y*y+z*z <= r*r:
                        blocks.append({"x": x, "y": 4*s+1+y, "z": z, "color": COLOR_HEX["leaves"]})
        # 花朵
        flower_colors = ["#e74c3c","#f1c40f","#9b59b6","#e67e22"]
        for i in range(10*s):
            import random
            fx = random.randint(-w+1, w-1)
            fz = random.randint(-w+1, w-1)
            blocks.append({"x": fx, "y": 1, "z": fz, "color": flower_colors[i % 4]})
    elif btype == "temple":
        w = 8 * s; h = 6 * s
        for step in range(4):
            sw = w - step * 2
            for x in range(-sw, sw+1, 1):
                for z in range(-sw, sw+1, 1):
                    if x == -sw or x == sw or z == -sw or z == sw:
                        blocks.append({"x": x, "y": step, "z": z, "color": hex_color})
        # 柱子
        for cx, cz in [(-w+2,-w+2),(w-2,-w+2),(-w+2,w-2),(w-2,w-2)]:
            for y in range(4, h+1):
                blocks.append({"x": cx, "y": y, "z": cz, "color": hex_color})
        # 屋顶
        for x in range(-w, w+1):
            for z in range(-w, w+1):
                blocks.append({"x": x, "y": h+1, "z": z, "color": hex_color})
    elif btype == "statue":
        h = 10 * s
        # 基座
        for x in range(-2, 3):
            for z in range(-2, 3):
                blocks.append({"x": x, "y": 0, "z": z, "color": hex_color})
                blocks.append({"x": x, "y": 1, "z": z, "color": hex_color})
        # 身体
        for y in range(2, h-2):
            blocks.append({"x": 0, "y": y, "z": 0, "color": hex_color})
        # 头
        r = 2
        for x in range(-r, r+1):
            for y in range(-r, r+1):
                for z in range(-r, r+1):
                    if x*x+y*y+z*z <= r*r:
                        blocks.append({"x": x, "y": h-2+y, "z": z, "color": hex_color})
    elif btype == "spaceship" or btype == "rocket":
        length = 8 * s
        for y in range(0, length):
            blocks.append({"x": 0, "y": y, "z": 0, "color": hex_color})
            blocks.append({"x": 1, "y": y, "z": 0, "color": hex_color})
            blocks.append({"x": -1, "y": y, "z": 0, "color": hex_color})
            blocks.append({"x": 0, "y": y, "z": 1, "color": hex_color})
            blocks.append({"x": 0, "y": y, "z": -1, "color": hex_color})
        # 机翼
        r = 4 * s
        for x in range(-r, r+1):
            blocks.append({"x": x, "y": 2*s, "z": 0, "color": hex_color})
            blocks.append({"x": x, "y": 3*s, "z": 0, "color": hex_color})
        # 头
        blocks.append({"x": 0, "y": length, "z": 0, "color": COLOR_HEX["glass"]})
    elif btype == "wall":
        length = 20 * s; h = 4 * s
        for x in range(0, length+1, 1):
            for y in range(0, h+1):
                blocks.append({"x": x, "y": y, "z": 0, "color": hex_color})
            if x % 2 == 0:
                blocks.append({"x": x, "y": h+1, "z": 0, "color": hex_color})
    elif btype == "spiral":
        h = 20 * s
        for y in range(0, h):
            angle = y * 0.5
            r = max(2, int(5 - y * 2 / h))
            x = int(math.cos(angle) * r)
            z = int(math.sin(angle) * r)
            blocks.append({"x": x, "y": y, "z": z, "color": hex_color})
    elif btype == "village":
        houses = max(3, int(5 * s))
        colors = [COLOR_HEX["wood"], COLOR_HEX["brick"], COLOR_HEX["sand"], COLOR_HEX["stone"]]
        for i in range(houses):
            angle = (i / houses) * math.pi * 2
            dist = 12 * s
            hx = int(math.cos(angle) * dist)
            hz = int(math.sin(angle) * dist)
            hc = colors[i % len(colors)]
            hw = 3 * s; hh = 4 * s
            for x in range(-hw, hw+1):
                blocks.append({"x": hx+x, "y": 0, "z": hz-hw, "color": hc})
                blocks.append({"x": hx+x, "y": hh, "z": hz-hw, "color": hc})
                blocks.append({"x": hx+x, "y": 0, "z": hz+hw, "color": hc})
                blocks.append({"x": hx+x, "y": hh, "z": hz+hw, "color": hc})
            for z in range(-hw, hw+1):
                blocks.append({"x": hx-hw, "y": 0, "z": hz+z, "color": hc})
                blocks.append({"x": hx-hw, "y": hh, "z": hz+z, "color": hc})
                blocks.append({"x": hx+hw, "y": 0, "z": hz+z, "color": hc})
                blocks.append({"x": hx+hw, "y": hh, "z": hz+z, "color": hc})
            # 屋顶
            for x in range(-hw-1, hw+2):
                for z in range(-hw-1, hw+2):
                    blocks.append({"x": hx+x, "y": hh+1, "z": hz+z, "color": COLOR_HEX["wood"]})
    elif btype == "shanghai":
        # 东方明珠塔
        for y in range(0, 30*s, 2):
            blocks.append({"x": 30, "y": y, "z": 0, "color": hex_color})
        r = 4 * s
        for x in range(-r, r+1):
            for y in range(-r, r+1):
                for z in range(-r, r+1):
                    if x*x+y*y+z*z <= r*r:
                        blocks.append({"x": 30+x, "y": 15*s+y, "z": z, "color": hex_color})
        # 上海中心
        for y in range(0, 50*s, 2):
            r2 = max(2, int(5 - y * 3 / (50*s)))
            for x in range(-r2, r2+1):
                blocks.append({"x": 38+x, "y": y, "z": 0, "color": hex_color})
    else:
        # 默认: 房子
        h = 4 * s; w = 5 * s
        for x in range(-w, w+1):
            blocks.append({"x": x, "y": 0, "z": -w, "color": hex_color})
            blocks.append({"x": x, "y": h, "z": -w, "color": hex_color})
            blocks.append({"x": x, "y": 0, "z": w, "color": hex_color})
            blocks.append({"x": x, "y": h, "z": w, "color": hex_color})
        for z in range(-w, w+1):
            blocks.append({"x": -w, "y": 0, "z": z, "color": hex_color})
            blocks.append({"x": -w, "y": h, "z": z, "color": hex_color})
            blocks.append({"x": w, "y": 0, "z": z, "color": hex_color})
            blocks.append({"x": w, "y": h, "z": z, "color": hex_color})
        for x in range(-w-1, w+2):
            for z in range(-w-1, w+2):
                blocks.append({"x": x, "y": h+1, "z": z, "color": COLOR_HEX["wood"]})

    # 限制方块数量防止浏览器卡死
    if len(blocks) > 3000:
        step = len(blocks) // 3000
        blocks = blocks[::step][:3000]

    return blocks
