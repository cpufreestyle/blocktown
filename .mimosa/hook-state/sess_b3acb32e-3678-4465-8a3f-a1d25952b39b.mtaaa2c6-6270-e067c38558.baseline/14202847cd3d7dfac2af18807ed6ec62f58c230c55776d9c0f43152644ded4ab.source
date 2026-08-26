#!/usr/bin/env python3
"""
Luanti Builder - 自然语言生成 Luanti/Minetest 建筑
跨平台 GUI 程序 (macOS / Linux / Windows)

用法: python3 luanti_builder.py
"""

import os
import sys
import platform
import re
import math
import textwrap
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext
except ImportError:
    print("错误: 需要安装 tkinter")
    print("  macOS: 自带 (系统 Python)")
    print("  Linux: sudo apt install python3-tk")
    print("  Windows: 自带")
    sys.exit(1)

# ============================================================
# 平台检测 - 获取 Luanti/Minetest 数据目录
# ============================================================

def get_minetest_dir():
    """返回平台对应的 Luanti/Minetest 用户数据目录"""
    system = platform.system()
    home = Path.home()

    if system == "Darwin":  # macOS
        # 优先用旧路径 minetest (Luanti 5.16 实际用这个)
        mt = home / "Library" / "Application Support" / "minetest"
        if mt.exists():
            return mt
        lu = home / "Library" / "Application Support" / "luanti"
        return lu if lu.exists() else mt
    elif system == "Linux":
        mt = home / ".minetest"
        if mt.exists():
            return mt
        lu = home / ".local" / "share" / "luanti"
        return lu if lu.exists() else mt
    elif system == "Windows":
        mt = home / "AppData" / "Roaming" / "minetest"
        if mt.exists():
            return mt
        lu = home / "AppData" / "Roaming" / "luanti"
        return lu if lu.exists() else mt
    else:
        return home / ".minetest"

def get_mods_dir():
    """返回 mods 目录"""
    return get_minetest_dir() / "mods"

# ============================================================
# 自然语言解析器
# ============================================================

class NLPParser:
    """解析自然语言描述，提取建筑参数"""

    # 建筑类型关键词
    BUILDING_TYPES = {
        "城堡": "castle", "城堡": "castle", "castle": "castle", "fortress": "castle",
        "房子": "house", "房屋": "house", "小屋": "house", "house": "house", "hut": "house", "cabin": "house",
        "塔": "tower", "tower": "tower", "高塔": "tower",
        "金字塔": "pyramid", "pyramid": "pyramid",
        "桥": "bridge", "桥梁": "bridge", "bridge": "bridge",
        "花园": "garden", "garden": "garden", "庭院": "garden",
        "神殿": "temple", "寺庙": "temple", "temple": "temple",
        "雕像": "statue", "statue": "statue", "雕塑": "statue",
        "喷泉": "fountain", "fountain": "fountain",
        "灯塔": "lighthouse", "lighthouse": "lighthouse",
        "城墙": "wall", "wall": "wall", "围墙": "wall",
        "树": "tree", "tree": "tree", "大树": "tree",
        "飞船": "spaceship", "spaceship": "spaceship", "火箭": "rocket",
        "蘑菇": "mushroom", "mushroom": "mushroom",
        "心形": "heart", "heart": "heart", "爱心": "heart",
        "球体": "sphere", "sphere": "sphere", "球": "sphere",
        "螺旋塔": "spiral", "spiral": "spiral",
        "上海": "shanghai", "shanghai": "shanghai",
        "村庄": "village", "village": "village",
    }

    # 颜色关键词
    COLOR_MAP = {
        "红色": "red", "红": "red", "red": "red",
        "蓝色": "blue", "蓝": "blue", "blue": "blue",
        "黄色": "yellow", "黄": "yellow", "yellow": "yellow",
        "绿色": "green", "绿": "green", "green": "green",
        "白色": "white", "白": "white", "white": "white",
        "黑色": "black", "黑": "black", "black": "black",
        "橙色": "orange", "橙": "orange", "orange": "orange",
        "紫色": "purple", "紫": "purple", "purple": "purple",
        "粉色": "pink", "粉": "pink", "pink": "pink",
        "青色": "cyan", "青": "cyan", "cyan": "cyan",
        "灰色": "gray", "灰": "gray", "gray": "gray",
        "金色": "yellow", "gold": "yellow",
    }

    # 尺寸关键词
    SIZE_MAP = {
        "巨大": 3, "超大": 3, "huge": 3, "giant": 3, "massive": 3,
        "大": 2, "大型": 2, "large": 2, "big": 2,
        "中等": 1, "medium": 1, "normal": 1,
        "小": 0, "小型": 0, "small": 0, "tiny": 0, "mini": 0,
    }

    # 材质关键词
    MATERIAL_MAP = {
        "石头": "stone", "石": "stone", "stone": "stone", "rock": "stone",
        "木头": "wood", "木": "wood", "wood": "wood", "wooden": "wood",
        "砖": "brick", "砖块": "brick", "brick": "brick",
        "沙子": "sand", "沙": "sand", "sand": "sand",
        "玻璃": "glass", "glass": "glass",
        "金属": "iron", "metal": "iron", "iron": "iron",
        "泥土": "dirt", "dirt": "dirt",
        "雪": "snow", "snow": "snow",
    }

    def parse(self, text):
        """解析自然语言文本，返回结构化参数"""
        text_lower = text.lower()
        result = {
            "type": None,
            "color": None,
            "size": 1,  # 默认中等
            "material": None,
            "features": [],
            "raw": text,
        }

        # 检测建筑类型
        for keyword, btype in self.BUILDING_TYPES.items():
            if keyword in text_lower:
                result["type"] = btype
                break

        # 检测颜色
        for keyword, color in self.COLOR_MAP.items():
            if keyword in text_lower:
                result["color"] = color
                break

        # 检测尺寸
        for keyword, size in self.SIZE_MAP.items():
            if keyword in text_lower:
                result["size"] = size
                break

        # 检测材质
        for keyword, mat in self.MATERIAL_MAP.items():
            if keyword in text_lower:
                result["material"] = mat
                break

        # 检测特征
        feature_keywords = {
            "塔楼": "towers", "tower": "towers", "尖塔": "towers",
            "护城河": "moat", "moat": "moat", "河": "moat",
            "花园": "garden", "garden": "garden",
            "门": "gate", "gate": "gate", "大门": "gate",
            "窗户": "windows", "window": "windows",
            "屋顶": "roof", "roof": "roof",
            "灯光": "lights", "light": "lights", "发光": "lights",
            "旗子": "flag", "flag": "flag", "旗帜": "flag",
            "楼梯": "stairs", "stair": "stairs",
        }
        for keyword, feature in feature_keywords.items():
            if keyword in text_lower and feature not in result["features"]:
                result["features"].append(feature)

        return result

# ============================================================
# Lua 代码生成器
# ============================================================

class LuaGenerator:
    """根据解析结果生成 Lua mod 代码"""

    def __init__(self):
        self.mod_name = "nl_builder"

    def generate(self, params):
        """生成完整的 Lua mod 代码"""
        btype = params["type"] or "house"
        color = params["color"] or "gray"
        size = params["size"]
        material = params["material"]
        features = params["features"]

        # 尺寸倍率
        size_mult = [0.6, 1.0, 1.5, 2.5][size]

        # 选择方块
        block = self._select_block(color, material)

        # 生成建筑函数
        builder_code = self._generate_builder(btype, block, size_mult, features)

        # 组装完整 mod
        lua = f"""-- nl_builder mod - 自然语言生成
-- 输入: {params["raw"]}
-- 类型: {btype}, 颜色: {color}, 尺寸: {size_mult}x, 特征: {", ".join(features) or "无"}

local B = "{block}"

-- 辅助函数
local function fill_box(pos, sx, sy, sz, ex, ey, ez, node_name)
    for x = sx, ex do
        for y = sy, ey do
            for z = sz, ez do
                minetest.set_node({{x = pos.x + x, y = pos.y + y, z = pos.z + z}}, {{name = node_name}})
            end
        end
    end
end

local function fill_shell(pos, sx, sy, sz, ex, ey, ez, node_name)
    for x = sx, ex do
        for y = sy, ey do
            for z = sz, ez do
                if x == sx or x == ex or y == sy or y == ey or z == sz or z == ez then
                    minetest.set_node({{x = pos.x + x, y = pos.y + y, z = pos.z + z}}, {{name = node_name}})
                else
                    minetest.set_node({{x = pos.x + x, y = pos.y + y, z = pos.z + z}}, {{name = "air"}})
                end
            end
        end
    end
end

local function fill_cylinder(pos, cx, cy, cz, radius, height, node_name)
    for y = 0, height - 1 do
        for x = -radius, radius do
            for z = -radius, radius do
                if x * x + z * z <= radius * radius then
                    minetest.set_node({{x = pos.x + cx + x, y = pos.y + cy + y, z = pos.z + cz + z}}, {{name = node_name}})
                end
            end
        end
    end
end

local function fill_sphere(pos, cx, cy, cz, radius, node_name)
    for x = -radius, radius do
        for y = -radius, radius do
            for z = -radius, radius do
                if x * x + y * y + z * z <= radius * radius then
                    minetest.set_node({{x = pos.x + cx + x, y = pos.y + cy + y, z = pos.z + cz + z}}, {{name = node_name}})
                end
            end
        end
    end
end

{builder_code}

-- 聊天命令
minetest.register_chatcommand("build", {{
    description = "用自然语言生成的建筑",
    func = function(name, param)
        local player = minetest.get_player_by_name(name)
        if not player then return false, "玩家不存在" end
        local pos = player:get_pos()
        pos.y = math.floor(pos.y)
        -- 找地面
        for dy = -3, 3 do
            local node = minetest.get_node_or_nil({{x = pos.x, y = pos.y + dy, z = pos.z}})
            local def = node and minetest.registered_nodes[node.name]
            if def and def.walkable and node.name ~= "air" then
                pos.y = pos.y + dy
                break
            end
        end
        -- 清空区域
        local r = math.ceil({size_mult} * 20)
        for x = -r, r do
            for y = 0, r do
                for z = -r, r do
                    minetest.set_node({{x = pos.x + x, y = pos.y + y, z = pos.z + z}}, {{name = "air"}})
                end
            end
        end
        build_structure(pos)
        return true, "建筑已生成！"
    end,
}})

print("[nl_builder] 自然语言建筑 mod 加载完成")
"""
        return lua

    def _select_block(self, color, material):
        """选择方块类型"""
        # 优先使用乐高积木 (如果 my_first_mod 存在)
        lego_colors = {
            "red": "my_first_mod:brick_red", "blue": "my_first_mod:brick_blue",
            "yellow": "my_first_mod:brick_yellow", "green": "my_first_mod:brick_green",
            "white": "my_first_mod:brick_white", "black": "my_first_mod:brick_black",
            "orange": "my_first_mod:brick_orange", "purple": "my_first_mod:brick_purple",
            "pink": "my_first_mod:brick_pink", "cyan": "my_first_mod:brick_cyan",
            "gray": "my_first_mod:brick_gray", "lime": "my_first_mod:brick_lime",
        }
        if color in lego_colors:
            return lego_colors[color]

        # 默认方块
        mat_blocks = {
            "stone": "default:stone", "wood": "default:wood",
            "brick": "default:brick", "sand": "default:sandstone",
            "glass": "default:glass", "iron": "default:steelblock",
            "dirt": "default:dirt", "snow": "default:snow",
        }
        if material in mat_blocks:
            return mat_blocks[material]

        return "default:stone"

    def _generate_builder(self, btype, block, size, features):
        """生成建筑函数代码"""
        s = size  # 尺寸倍率

        if btype == "castle":
            return self._gen_castle(block, s, features)
        elif btype == "house":
            return self._gen_house(block, s, features)
        elif btype == "tower":
            return self._gen_tower(block, s, features)
        elif btype == "pyramid":
            return self._gen_pyramid(block, s)
        elif btype == "bridge":
            return self._gen_bridge(block, s)
        elif btype == "garden":
            return self._gen_garden(block, s)
        elif btype == "temple":
            return self._gen_temple(block, s)
        elif btype == "statue":
            return self._gen_statue(block, s)
        elif btype == "fountain":
            return self._gen_fountain(block, s)
        elif btype == "lighthouse":
            return self._gen_lighthouse(block, s)
        elif btype == "wall":
            return self._gen_wall(block, s)
        elif btype == "tree":
            return self._gen_tree(block, s)
        elif btype == "spaceship" or btype == "rocket":
            return self._gen_spaceship(block, s)
        elif btype == "mushroom":
            return self._gen_mushroom(block, s)
        elif btype == "heart":
            return self._gen_heart(block, s)
        elif btype == "sphere":
            return self._gen_sphere(block, s)
        elif btype == "spiral":
            return self._gen_spiral(block, s)
        elif btype == "shanghai":
            return self._gen_shanghai(block, s)
        elif btype == "village":
            return self._gen_village(block, s)
        else:
            return self._gen_house(block, s, features)

    def _gen_castle(self, block, s, features):
        h = int(8 * s)
        w = int(10 * s)
        has_towers = "towers" in features or True
        has_moat = "moat" in features
        has_gate = "gate" in features or True
        has_lights = "lights" in features
        return textwrap.dedent(f"""\
            local function build_structure(pos)
                local h = {h}
                local w = {w}
                -- 城墙
                fill_shell(pos, -w, 0, -w, w, h, w, B)
                -- 四角塔楼
                for _, corner in ipairs({{{{-w, -w}}, {{w, -w}}, {{-w, w}}, {{w, w}}}}) do
                    fill_cylinder(pos, corner[1], 0, corner[2], math.ceil({s}*2), h + math.ceil({s}*4), B)
                    -- 塔顶
                    fill_sphere(pos, corner[1], h + math.ceil({s}*4), corner[2], math.ceil({s}*2), B)
                end
                -- 城门
                fill_box(pos, -2, 0, -w, 2, math.ceil({s}*3), -w, "air")
                -- 地板
                fill_box(pos, -w+1, 0, -w+1, w-1, 0, w-1, B)
                {"fill_box(pos, -w-2, -1, -w-2, w+2, -1, w+2, 'default:water_source') -- 护城河" if has_moat else ""}
                {"for tx = -w, w, 4 do minetest.set_node({{x=pos.x+tx, y=pos.y+h+1, z=pos.z}}, {{name='my_first_mod:brick_glow'}}) end -- 灯光" if has_lights else ""}
            end""")

    def _gen_house(self, block, s, features):
        h = int(4 * s)
        w = int(5 * s)
        has_roof = "roof" in features or True
        has_windows = "windows" in features
        has_lights = "lights" in features
        roof = "default:wood" if block != "default:wood" else "default:stone"
        return textwrap.dedent(f"""\
            local function build_structure(pos)
                local h = {h}
                local w = {w}
                fill_shell(pos, -w, 0, -w, w, h, w, B)
                -- 地板
                fill_box(pos, -w+1, 0, -w+1, w-1, 0, w-1, B)
                -- 门
                fill_box(pos, -1, 0, -w, 1, math.max(2, math.ceil({s}*2)), -w, "air")
                -- 屋顶
                {"fill_box(pos, -w-1, h+1, -w-1, w+1, h+1, w+1, '" + roof + "') -- 屋顶" if has_roof else ""}
                -- 窗户
                {"minetest.set_node({{x=pos.x-w, y=pos.y+math.ceil(h/2), z=pos.z}}, {{name='default:glass'}})" if has_windows else ""}
                {"minetest.set_node({{x=pos.x+w, y=pos.y+math.ceil(h/2), z=pos.z}}, {{name='default:glass'}})" if has_windows else ""}
                -- 灯光
                {"minetest.set_node({{x=pos.x, y=pos.y+h-1, z=pos.z}}, {{name='my_first_mod:brick_glow'}})" if has_lights else ""}
            end""")

    def _gen_tower(self, block, s, features):
        h = int(20 * s)
        r = max(2, int(3 * s))
        return textwrap.dedent(f"""\
            local function build_structure(pos)
                local h = {h}
                local r = {r}
                -- 主塔
                fill_cylinder(pos, 0, 0, 0, r, h, B)
                -- 顶部尖塔
                for y = 0, math.ceil({s}*5) do
                    local rr = math.max(1, r - math.floor(y * r / (math.ceil({s}*5)+1)))
                    fill_cylinder(pos, 0, h+y, 0, rr, 1, B)
                end
                -- 顶部灯光
                minetest.set_node({{x = pos.x, y = pos.y + h + math.ceil({s}*5) + 1, z = pos.z}}, {{name = "my_first_mod:brick_glow"}})
            end""")

    def _gen_pyramid(self, block, s):
        h = int(10 * s)
        return textwrap.dedent(f"""\
            local function build_structure(pos)
                local h = {h}
                for y = 0, h do
                    local r = h - y
                    fill_box(pos, -r, y, -r, r, y, r, B)
                end
            end""")

    def _gen_bridge(self, block, s):
        length = int(20 * s)
        h = int(5 * s)
        return textwrap.dedent(f"""\
            local function build_structure(pos)
                local length = {length}
                local h = {h}
                -- 桥面
                fill_box(pos, 0, h, -3, length, h, 3, B)
                -- 两个桥墩
                fill_box(pos, 0, 0, -3, 0, h-1, 3, B)
                fill_box(pos, length, 0, -3, length, h-1, 3, B)
                -- 斜拉索
                for x = 0, length, 2 do
                    local dy = math.floor(math.abs(x - length/2) * h / (length/2))
                    if dy > 0 and dy < h then
                        minetest.set_node({{x = pos.x + x, y = pos.y + dy, z = pos.z}}, {{name = "default:fence_wood"}})
                    end
                end
            end""")

    def _gen_garden(self, block, s):
        w = int(8 * s)
        return textwrap.dedent(f"""\
            local function build_structure(pos)
                local w = {w}
                -- 草地
                fill_box(pos, -w, 0, -w, w, 0, w, "default:dirt_with_grass")
                -- 花朵
                for i = 1, math.ceil({s}*10) do
                    local fx = math.random(-w+1, w-1)
                    local fz = math.random(-w+1, w-1)
                    local flowers = {{"flowers:rose", "flowers:tulip", "flowers:dandelion_yellow", "flowers:geranium"}}
                    minetest.set_node({{x = pos.x + fx, y = pos.y + 1, z = pos.z + fz}}, {{name = flowers[math.random(1,4)]}})
                end
                -- 中央树
                fill_cylinder(pos, 0, 1, 0, 1, math.ceil({s}*4), "default:tree")
                fill_sphere(pos, 0, math.ceil({s}*4)+1, 0, math.ceil({s}*3), "default:leaves")
                -- 围栏
                for x = -w, w do
                    minetest.set_node({{x = pos.x + x, y = pos.y + 1, z = pos.z - w}}, {{name = "default:fence_wood"}})
                    minetest.set_node({{x = pos.x + x, y = pos.y + 1, z = pos.z + w}}, {{name = "default:fence_wood"}})
                end
                for z = -w, w do
                    minetest.set_node({{x = pos.x - w, y = pos.y + 1, z = pos.z + z}}, {{name = "default:fence_wood"}})
                    minetest.set_node({{x = pos.x + w, y = pos.y + 1, z = pos.z + z}}, {{name = "default:fence_wood"}})
                end
            end""")

    def _gen_temple(self, block, s):
        w = int(8 * s)
        h = int(6 * s)
        return textwrap.dedent(f"""\
            local function build_structure(pos)
                local w = {w}
                local h = {h}
                -- 基座 (阶梯式)
                for step = 0, 3 do
                    local sw = w - step * 2
                    fill_box(pos, -sw, step, -sw, sw, step, sw, B)
                end
                -- 柱子
                for _, corner in ipairs({{{{-w+2, -w+2}}, {{w-2, -w+2}}, {{-w+2, w-2}}, {{w-2, w-2}}}}) do
                    fill_box(pos, corner[1], 4, corner[2], corner[1], h, corner[2], B)
                end
                -- 屋顶
                fill_box(pos, -w+1, h+1, -w+1, w-1, h+1, w-1, B)
                fill_box(pos, -w, h+2, -w, w, h+2, w, B)
                -- 内部灯光
                minetest.set_node({{x = pos.x, y = pos.y + 5, z = pos.z}}, {{name = "my_first_mod:brick_glow"}})
            end""")

    def _gen_statue(self, block, s):
        h = int(10 * s)
        return textwrap.dedent(f"""\
            local function build_structure(pos)
                local h = {h}
                -- 基座
                fill_box(pos, -2, 0, -2, 2, 2, 2, B)
                -- 身体
                fill_box(pos, -1, 3, -1, 1, h-2, 1, B)
                -- 头
                fill_sphere(pos, 0, h-1, 0, 2, B)
                -- 手臂
                fill_box(pos, -3, math.floor(h/2), 0, -2, math.floor(h/2)+2, 0, B)
                fill_box(pos, 2, math.floor(h/2), 0, 3, math.floor(h/2)+2, 0, B)
            end""")

    def _gen_fountain(self, block, s):
        r = int(4 * s)
        return textwrap.dedent(f"""\
            local function build_structure(pos)
                local r = {r}
                -- 底座
                fill_cylinder(pos, 0, 0, 0, r, 1, B)
                -- 水池
                fill_cylinder(pos, 0, 1, 0, r-1, 1, "default:water_source")
                -- 中央柱
                fill_cylinder(pos, 0, 2, 0, 1, math.ceil({s}*3), B)
                -- 顶部水
                fill_cylinder(pos, 0, math.ceil({s}*3)+2, 0, 2, 1, "default:water_source")
            end""")

    def _gen_lighthouse(self, block, s):
        h = int(15 * s)
        r = max(2, int(3 * s))
        return textwrap.dedent(f"""\
            local function build_structure(pos)
                local h = {h}
                local r = {r}
                -- 塔身 (红白条纹)
                for y = 0, h do
                    local b = (math.floor(y / 3) % 2 == 0) and B or "default:white"
                    fill_cylinder(pos, 0, y, 0, r, 1, b)
                end
                -- 灯室
                fill_cylinder(pos, 0, h+1, 0, r-1, 2, "default:glass")
                -- 灯
                minetest.set_node({{x = pos.x, y = pos.y + h + 2, z = pos.z}}, {{name = "my_first_mod:brick_glow"}})
            end""")

    def _gen_wall(self, block, s):
        length = int(20 * s)
        h = int(4 * s)
        return textwrap.dedent(f"""\
            local function build_structure(pos)
                local length = {length}
                local h = {h}
                fill_box(pos, 0, 0, -1, length, h, 1, B)
                -- 城垛
                for x = 0, length, 2 do
                    minetest.set_node({{x = pos.x + x, y = pos.y + h + 1, z = pos.z}}, {{name = B}})
                end
            end""")

    def _gen_tree(self, block, s):
        h = int(8 * s)
        r = int(4 * s)
        return textwrap.dedent(f"""\
            local function build_structure(pos)
                local h = {h}
                local r = {r}
                -- 树干
                fill_cylinder(pos, 0, 0, 0, 1, h, "default:tree")
                -- 树冠
                fill_sphere(pos, 0, h, 0, r, "default:leaves")
                fill_sphere(pos, 0, h+r, 0, r-1, "default:leaves")
            end""")

    def _gen_spaceship(self, block, s):
        return textwrap.dedent(f"""\
            local function build_structure(pos)
                local r = math.ceil({s}*4)
                -- 机身
                fill_cylinder(pos, 0, 0, 0, 2, math.ceil({s}*8), B)
                -- 机头
                fill_sphere(pos, 0, math.ceil({s}*8), 0, 2, B)
                -- 机翼
                fill_box(pos, -r, 2, -1, r, 3, 1, B)
                -- 引擎
                fill_cylinder(pos, -2, 0, 0, 1, 2, "default:furnace_active")
                fill_cylinder(pos, 2, 0, 0, 1, 2, "default:furnace_active")
                -- 窗户
                fill_box(pos, -1, math.ceil({s}*6), 0, 1, math.ceil({s}*6), 0, "default:glass")
            end""")

    def _gen_mushroom(self, block, s):
        h = int(5 * s)
        r = max(2, int(3 * s))
        return textwrap.dedent(f"""\
            local function build_structure(pos)
                local h = {h}
                local r = {r}
                -- 茎
                fill_cylinder(pos, 0, 0, 0, 1, h, "default:white")
                -- 蘑菇帽
                fill_sphere(pos, 0, h, 0, r, B)
                -- 底部切平
                fill_box(pos, -r, 0, -r, r, 0, r, "air")
            end""")

    def _gen_heart(self, block, s):
        return textwrap.dedent(f"""\
            local function build_structure(pos)
                local s = math.ceil({s})
                -- 心形像素图 11x9
                local heart = {{
                    ".##...##.",
                    "###############".sub(1,9),
                    "#########",
                    "#########",
                    ".#######.",
                    "..#####..",
                    "...###...",
                    "....#....",
                }}
                local pattern = {{
                    ".##...##.",
                    "#########",
                    "#########",
                    "#########",
                    ".#######.",
                    "..#####..",
                    "...###...",
                    "....#....",
                }}
                for row = 1, #pattern do
                    local line = pattern[row]
                    for col = 1, #line do
                        if line:sub(col, col) == "#" then
                            for dx = 0, s-1 do
                                for dy = 0, s-1 do
                                    minetest.set_node({{
                                        x = pos.x + (col-1)*s + dx,
                                        y = pos.y + (#pattern - row)*s + dy,
                                        z = pos.z
                                    }}, {{name = B}})
                                end
                            end
                        end
                    end
                end
            end""")

    def _gen_sphere(self, block, s):
        r = max(3, int(6 * s))
        return textwrap.dedent(f"""\
            local function build_structure(pos)
                fill_sphere(pos, 0, {r}, 0, {r}, B)
            end""")

    def _gen_spiral(self, block, s):
        h = int(20 * s)
        return textwrap.dedent(f"""\
            local function build_structure(pos)
                local h = {h}
                for y = 0, h do
                    local angle = y * 0.5
                    local r = math.max(2, math.floor(5 - y * 2 / h))
                    local x = math.floor(math.cos(angle) * r)
                    local z = math.floor(math.sin(angle) * r)
                    minetest.set_node({{x = pos.x + x, y = pos.y + y, z = pos.z + z}}, {{name = B}})
                end
            end""")

    def _gen_shanghai(self, block, s):
        return textwrap.dedent(f"""\
            local function build_structure(pos)
                -- 东方明珠塔 (简化版)
                fill_cylinder(pos, 30, 0, 0, 2, math.ceil({s}*30), B)
                fill_sphere(pos, 30, math.ceil({s}*15), 0, math.ceil({s}*4), B)
                fill_sphere(pos, 30, math.ceil({s}*25), 0, math.ceil({s}*3), B)
                -- 上海中心大厦
                for y = 0, math.ceil({s}*50) do
                    local r = math.max(2, math.floor(5 - y * 3 / math.ceil({s}*50)))
                    for x = -r, r do
                        for z = -r, r do
                            if math.abs(x) == r or math.abs(z) == r then
                                minetest.set_node({{x = pos.x + 38 + x, y = pos.y + y, z = pos.z + z}}, {{name = B}})
                            end
                        end
                    end
                end
                -- 金茂大厦 (宝塔式)
                for section = 0, 5 do
                    local r = math.max(1, 4 - section)
                    local y0 = section * math.ceil({s}*7)
                    fill_box(pos, 32-r, y0, -r, 32+r, y0 + math.ceil({s}*6), r, B)
                end
            end""")

    def _gen_village(self, block, s):
        return textwrap.dedent(f"""\
            local function build_structure(pos)
                local houses = math.max(3, math.ceil({s}*5))
                for i = 1, houses do
                    local angle = (i / houses) * math.pi * 2
                    local dist = math.ceil({s}*12)
                    local hx = math.floor(math.cos(angle) * dist)
                    local hz = math.floor(math.sin(angle) * dist)
                    local colors = {{"default:wood", "default:brick", "default:sandstone", "default:stone"}}
                    local hb = colors[((i-1) % #colors) + 1]
                    local h = math.ceil({s}*4)
                    local w = math.ceil({s}*3)
                    fill_shell(pos, hx-w, 0, hz-w, hx+w, h, hz+w, hb)
                    fill_box(pos, hx-w-1, h+1, hz-w-1, hx+w+1, h+1, hz+w+1, "default:wood")
                    fill_box(pos, hx-1, 0, hz-w, hx+1, 2, hz-w, "air")
                end
            end""")

# ============================================================
# GUI 应用
# ============================================================

class LuantiBuilderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Luanti 自然语言建筑生成器")
        self.root.geometry("700x600")
        self.root.minsize(600, 500)

        self.parser = NLPParser()
        self.generator = LuaGenerator()

        self._build_ui()
        self._check_minetest_dir()

    def _build_ui(self):
        # 主容器
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        # 标题
        ttk.Label(main, text="🏗️ Luanti 自然语言建筑生成器",
                  font=("Arial", 16, "bold")).pack(pady=(0, 8))

        # Luanti 路径显示
        path_frame = ttk.Frame(main)
        path_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(path_frame, text="Mod 目录:").pack(side=tk.LEFT)
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var, state="readonly")
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        ttk.Button(path_frame, text="浏览", command=self._browse_path).pack(side=tk.RIGHT)

        # 输入框
        ttk.Label(main, text="描述你想要的建筑:").pack(anchor=tk.W)
        self.input_text = tk.Text(main, height=3, font=("Arial", 13), wrap=tk.WORD)
        self.input_text.pack(fill=tk.X, pady=(4, 8))
        self.input_text.insert("1.0", "建一个红色的城堡，有塔楼和护城河")

        # 按钮区
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=4)
        ttk.Button(btn_frame, text="🔍 解析", command=self._parse_input).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="📋 生成 Lua", command=self._generate_lua).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="💾 安装到 Luanti", command=self._install_mod).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="🚀 生成并安装", command=self._generate_and_install).pack(side=tk.LEFT, padx=4)

        # 解析结果
        ttk.Label(main, text="解析结果:").pack(anchor=tk.W, pady=(8, 0))
        self.result_text = tk.Text(main, height=5, font=("Courier", 11), wrap=tk.WORD, bg="#f0f0f0")
        self.result_text.pack(fill=tk.X, pady=4)

        # Lua 代码预览
        ttk.Label(main, text="生成的 Lua 代码:").pack(anchor=tk.W, pady=(8, 0))
        self.code_text = scrolledtext.ScrolledText(main, height=12, font=("Courier", 10), wrap=tk.NONE)
        self.code_text.pack(fill=tk.BOTH, expand=True, pady=4)

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(main, textvariable=self.status_var, relief=tk.SUNKEN).pack(fill=tk.X, pady=(4, 0))

        # 示例提示
        examples = [
            "建一个红色的城堡，有塔楼和护城河",
            "建造一座大型金字塔",
            "做一个发光的灯塔",
            "建一座桥",
            "建造一个大型花园",
            "做一个爱心",
            "建一座神殿",
            "建造一棵巨大的树",
            "做一个飞船",
            "建一个村庄",
        ]
        ttk.Label(main, text="示例: " + " | ".join(examples[:5]),
                  font=("Arial", 9), foreground="gray").pack(anchor=tk.W, pady=(4, 0))

    def _check_minetest_dir(self):
        mods_dir = get_mods_dir()
        self.path_var.set(str(mods_dir))
        if not mods_dir.exists():
            self._set_status(f"⚠️ 目录不存在: {mods_dir}")
        else:
            self._set_status("✅ 目录就绪")

    def _browse_path(self):
        from tkinter import filedialog
        path = filedialog.askdirectory(title="选择 Luanti/Minetest mods 目录")
        if path:
            self.path_var.set(path)

    def _set_status(self, msg):
        self.status_var.set(msg)
        self.root.update_idletasks()

    def _parse_input(self):
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("提示", "请输入建筑描述")
            return

        params = self.parser.parse(text)
        self.last_params = params

        result = f"类型: {params['type'] or '未知'}\n"
        result += f"颜色: {params['color'] or '默认'}\n"
        result += f"尺寸: {['小', '中', '大', '巨大'][params['size']]}\n"
        result += f"材质: {params['material'] or '默认'}\n"
        result += f"特征: {', '.join(params['features']) if params['features'] else '无'}\n"
        result += f"原始输入: {params['raw']}"

        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", result)
        self._set_status("✅ 解析完成")

    def _generate_lua(self):
        if not hasattr(self, 'last_params') or not self.last_params:
            self._parse_input()
            if not hasattr(self, 'last_params') or not self.last_params:
                return

        lua_code = self.generator.generate(self.last_params)
        self.last_lua = lua_code

        self.code_text.delete("1.0", tk.END)
        self.code_text.insert("1.0", lua_code)
        self._set_status("✅ Lua 代码生成完成")

    def _install_mod(self):
        if not hasattr(self, 'last_lua'):
            messagebox.showwarning("提示", "请先生成 Lua 代码")
            return

        mods_dir = Path(self.path_var.get())
        if not mods_dir.exists():
            messagebox.showerror("错误", f"目录不存在: {mods_dir}")
            return

        mod_dir = mods_dir / "nl_builder"
        mod_dir.mkdir(parents=True, exist_ok=True)

        # 写 mod.conf
        (mod_dir / "mod.conf").write_text(
            "name = nl_builder\n"
            "description = 自然语言生成的建筑\n"
            "depends = default\n"
        )

        # 写 init.lua
        (mod_dir / "init.lua").write_text(self.last_lua, encoding="utf-8")

        self._set_status(f"✅ 已安装到 {mod_dir}")
        messagebox.showinfo("成功",
            f"Mod 已安装到:\n{mod_dir}\n\n"
            f"在 Luanti 中:\n"
            f"1. 确保世界启用了 nl_builder mod\n"
            f"2. 进入游戏后输入 /build 即可生成建筑\n"
            f"3. 建筑会在你脚下生成")

    def _generate_and_install(self):
        self._parse_input()
        self._generate_lua()
        self._install_mod()

# ============================================================
# 主入口
# ============================================================

def main():
    root = tk.Tk()
    app = LuantiBuilderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
