#!/usr/bin/env python3
"""
Luanti Builder - 自然语言生成 Luanti/Minetest 建筑 (Web版)
跨平台: macOS / Linux / Windows
纯 Python 标准库，无需安装任何依赖

用法: python3 luanti_builder_web.py
浏览器打开 http://localhost:8765
"""

import os
import sys
import json
import platform
import re
import math
import textwrap
import urllib.request
import urllib.error
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

# ============================================================
# 平台检测
# ============================================================

def get_minetest_dir():
    system = platform.system()
    home = Path.home()
    if system == "Darwin":
        for p in [home/"Library"/"Application Support"/"minetest",
                  home/"Library"/"Application Support"/"luanti"]:
            if p.exists():
                return p
        return home/"Library"/"Application Support"/"minetest"
    elif system == "Linux":
        for p in [home/".minetest", home/".local"/"share"/"luanti"]:
            if p.exists():
                return p
        return home/".minetest"
    elif system == "Windows":
        for p in [home/"AppData"/"Roaming"/"minetest",
                  home/"AppData"/"Roaming"/"luanti"]:
            if p.exists():
                return p
        return home/"AppData"/"Roaming"/"minetest"
    return home/".minetest"

# ============================================================
# NLP 解析器
# ============================================================

BUILDING_TYPES = {
    "城堡":"castle","castle":"castle","fortress":"castle",
    "房子":"house","房屋":"house","小屋":"house","house":"house","hut":"house","cabin":"house",
    "塔":"tower","tower":"tower","高塔":"tower",
    "金字塔":"pyramid","pyramid":"pyramid",
    "桥":"bridge","桥梁":"bridge","bridge":"bridge",
    "花园":"garden","garden":"garden","庭院":"garden",
    "神殿":"temple","寺庙":"temple","temple":"temple",
    "雕像":"statue","statue":"statue","雕塑":"statue",
    "喷泉":"fountain","fountain":"fountain",
    "灯塔":"lighthouse","lighthouse":"lighthouse",
    "城墙":"wall","wall":"wall","围墙":"wall",
    "树":"tree","tree":"tree","大树":"tree",
    "飞船":"spaceship","spaceship":"spaceship","火箭":"rocket",
    "蘑菇":"mushroom","mushroom":"mushroom",
    "心形":"heart","heart":"heart","爱心":"heart",
    "球体":"sphere","sphere":"sphere","球":"sphere",
    "螺旋":"spiral","spiral":"spiral",
    "上海":"shanghai","shanghai":"shanghai",
    "村庄":"village","village":"village",
}

COLOR_MAP = {
    "红色":"red","红":"red","red":"red",
    "蓝色":"blue","蓝":"blue","blue":"blue",
    "黄色":"yellow","黄":"yellow","yellow":"yellow","金色":"yellow","gold":"yellow",
    "绿色":"green","绿":"green","green":"green",
    "白色":"white","白":"white","white":"white",
    "黑色":"black","黑":"black","black":"black",
    "橙色":"orange","橙":"orange","orange":"orange",
    "紫色":"purple","紫":"purple","purple":"purple",
    "粉色":"pink","粉":"pink","pink":"pink",
    "青色":"cyan","青":"cyan","cyan":"cyan",
    "灰色":"gray","灰":"gray","gray":"gray",
}

SIZE_MAP = {
    "巨大":3,"超大":3,"huge":3,"giant":3,"massive":3,
    "大":2,"大型":2,"large":2,"big":2,
    "中等":1,"medium":1,"normal":1,
    "小":0,"小型":0,"small":0,"tiny":0,"mini":0,
}

MATERIAL_MAP = {
    "石头":"stone","石":"stone","stone":"stone","rock":"stone",
    "木头":"wood","木":"wood","wood":"wood","wooden":"wood",
    "砖":"brick","砖块":"brick","brick":"brick",
    "沙":"sand","沙子":"sand","sand":"sand",
    "玻璃":"glass","glass":"glass",
    "金属":"iron","metal":"iron","iron":"iron",
    "泥土":"dirt","dirt":"dirt",
    "雪":"snow","snow":"snow",
}

FEATURES_MAP = {
    "塔楼":"towers","tower":"towers","尖塔":"towers",
    "护城河":"moat","moat":"moat",  # 不再生成水，只标记特征
    "花园":"garden","garden":"garden",
    "大门":"gate","gate":"gate","门":"gate",
    "窗户":"windows","window":"windows",
    "屋顶":"roof","roof":"roof",
    "灯光":"lights","light":"lights","发光":"lights",
    "旗":"flag","flag":"flag","旗帜":"flag",
    "楼梯":"stairs","stair":"stairs",
}

def parse_input(text):
    tl = text.lower()
    result = {"type":None,"color":None,"size":1,"material":None,"features":[],"raw":text}
    for k,v in BUILDING_TYPES.items():
        if k in tl: result["type"]=v; break
    for k,v in COLOR_MAP.items():
        if k in tl: result["color"]=v; break
    for k,v in SIZE_MAP.items():
        if k in tl: result["size"]=v; break
    for k,v in MATERIAL_MAP.items():
        if k in tl: result["material"]=v; break
    for k,v in FEATURES_MAP.items():
        if k in tl and v not in result["features"]: result["features"].append(v)
    return result

# ============================================================
# Lua 生成器
# ============================================================

def select_block(color, material):
    lego = {"red":"my_first_mod:brick_red","blue":"my_first_mod:brick_blue",
        "yellow":"my_first_mod:brick_yellow","green":"my_first_mod:brick_green",
        "white":"my_first_mod:brick_white","black":"my_first_mod:brick_black",
        "orange":"my_first_mod:brick_orange","purple":"my_first_mod:brick_purple",
        "pink":"my_first_mod:brick_pink","cyan":"my_first_mod:brick_cyan",
        "gray":"my_first_mod:brick_gray"}
    if color in lego: return lego[color]
    mats = {"stone":"default:stone","wood":"default:wood","brick":"default:brick",
        "sand":"default:sandstone","glass":"default:glass","iron":"default:steelblock",
        "dirt":"default:dirt","snow":"default:snow"}
    if material in mats: return mats[material]
    return "default:stone"

def gen_lua(params):
    btype = params["type"] or "house"
    color = params["color"] or "gray"
    size = params["size"]
    material = params["material"]
    features = params["features"]
    sm = [0.6,1.0,1.5,2.5][size]
    block = select_block(color, material)
    builder = gen_builder(btype, block, sm, features)

    lua = f'''-- nl_builder mod - 自然语言生成
-- 输入: {params["raw"]}
-- 类型: {btype}, 颜色: {color}, 尺寸: {sm}x

local B = "{block}"

local function fill_box(pos, sx, sy, sz, ex, ey, ez, node_name)
    for x = sx, ex do for y = sy, ey do for z = sz, ez do
        minetest.set_node({{x=pos.x+x, y=pos.y+y, z=pos.z+z}}, {{name=node_name}})
    end end end
end

local function fill_shell(pos, sx, sy, sz, ex, ey, ez, node_name)
    for x = sx, ex do for y = sy, ey do for z = sz, ez do
        if x==sx or x==ex or y==sy or y==ey or z==sz or z==ez then
            minetest.set_node({{x=pos.x+x, y=pos.y+y, z=pos.z+z}}, {{name=node_name}})
        end
    end end end
end

local function fill_cylinder(pos, cx, cy, cz, radius, height, node_name)
    for y=0, height-1 do for x=-radius, radius do for z=-radius, radius do
        if x*x+z*z <= radius*radius then
            minetest.set_node({{x=pos.x+cx+x, y=pos.y+cy+y, z=pos.z+cz+z}}, {{name=node_name}})
        end
    end end end
end

local function fill_sphere(pos, cx, cy, cz, radius, node_name)
    for x=-radius, radius do for y=-radius, radius do for z=-radius, radius do
        if x*x+y*y+z*z <= radius*radius then
            minetest.set_node({{x=pos.x+cx+x, y=pos.y+cy+y, z=pos.z+cz+z}}, {{name=node_name}})
        end
    end end end
end

{builder}

minetest.register_chatcommand("build", {{
    description = "生成自然语言建筑",
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
        -- 填平地面（y=0 的水和空气替换为石头），清除 y=1 以上
        local r = math.ceil({sm} * 20)
        for x = -r, r do for z = -r, r do
            -- 填平 y=0 的水和坑
            local n = minetest.get_node_or_nil({{x=pos.x+x, y=pos.y, z=pos.z+z}})
            if n and (n.name == "air" or n.name == "default:water_source" or n.name == "default:water_flowing" or n.name == "default:lava_source" or n.name == "default:lava_flowing") then
                minetest.set_node({{x=pos.x+x, y=pos.y, z=pos.z+z}}, {{name="default:stone"}})
            end
        end end
        -- 清除地面上方
        for x = -r, r do for y = 1, r do for z = -r, r do
            minetest.set_node({{x=pos.x+x, y=pos.y+y, z=pos.z+z}}, {{name="air"}})
        end end end
        build_structure(pos)
        return true, "建筑已生成！"
    end,
}})

print("[nl_builder] 自然语言建筑 mod 加载完成")
'''
    return lua

def gen_builder(btype, B, s, features):
    h = int(8*s); w = int(10*s)
    if btype == "castle":
        towers = "towers" in features or True
        moat = False  # 不生成护城河水塘
        lights = "lights" in features
        moat_code = ""  # 不生成水塘
        lights_code = "for tx=-w,w,4 do minetest.set_node({x=pos.x+tx,y=pos.y+h+1,z=pos.z},{name='my_first_mod:brick_glow'}) end" if lights else ""
        return f"""local function build_structure(pos)
    local h = {h} local w = {w}
    fill_shell(pos, -w, 1, -w, w, h+1, w, B)
    for _, c in ipairs({{{{-w,-w}},{{w,-w}},{{-w,w}},{{w,w}}}}) do
        fill_cylinder(pos, c[1], 1, c[2], math.ceil({s}*2), h+math.ceil({s}*4), B)
        fill_sphere(pos, c[1], h+math.ceil({s}*4)+1, c[2], math.ceil({s}*2), B)
    end
    fill_box(pos, -2, 1, -w, 2, math.ceil({s}*3), -w, "air")
    {moat_code}
    {lights_code}
end"""
    elif btype == "house":
        h2 = int(4*s); w2 = int(5*s)
        roof = "default:wood" if B != "default:wood" else "default:stone"
        return f"""local function build_structure(pos)
    local h = {h2} local w = {w2}
    fill_shell(pos, -w, 1, -w, w, h+1, w, B)
    fill_box(pos, -1, 1, -w, 1, math.max(2,math.ceil({s}*2)), -w, "air")
    fill_box(pos, -w-1, h+2, -w-1, w+1, h+2, w+1, "{roof}")
    minetest.set_node({{x=pos.x, y=pos.y+h, z=pos.z}}, {{name="my_first_mod:brick_glow"}})
end"""
    elif btype == "tower":
        th = int(20*s); tr = max(2, int(3*s))
        return f"""local function build_structure(pos)
    fill_cylinder(pos, 0, 1, 0, {tr}, {th}, B)
    for y=0, math.ceil({s}*5) do
        local rr = math.max(1, {tr}-math.floor(y*{tr}/(math.ceil({s}*5)+1)))
        fill_cylinder(pos, 0, {th}+y+1, 0, rr, 1, B)
    end
    minetest.set_node({{x=pos.x, y=pos.y+{th}+math.ceil({s}*5)+1, z=pos.z}}, {{name="my_first_mod:brick_glow"}})
end"""
    elif btype == "pyramid":
        ph = int(10*s)
        return f"""local function build_structure(pos)
    local h = {ph}
    for y=0, h do
        local r = h - y
        fill_box(pos, -r, y, -r, r, y, r, B)
    end
end"""
    elif btype == "bridge":
        bl = int(20*s); bh = int(5*s)
        return f"""local function build_structure(pos)
    local length = {bl} local h = {bh}
    fill_box(pos, 0, h, -3, length, h, 3, B)
    fill_box(pos, 0, 1, -3, 0, h, 3, B)
    fill_box(pos, length, 0, -3, length, h-1, 3, B)
    for x=0, length, 2 do
        local dy = math.floor(math.abs(x-length/2)*h/(length/2))
        if dy>0 and dy<h then
            minetest.set_node({{x=pos.x+x, y=pos.y+dy, z=pos.z}}, {{name="default:fence_wood"}})
        end
    end
end"""
    elif btype == "garden":
        gw = int(8*s)
        return f"""local function build_structure(pos)
    local w = {gw}
    -- 不修改地面，只在上方放置花朵和围栏
    for i=1, math.ceil({s}*10) do
        local fx = math.random(-w+1, w-1) local fz = math.random(-w+1, w-1)
        local fl = {{"flowers:rose","flowers:tulip","flowers:dandelion_yellow","flowers:geranium"}}
        minetest.set_node({{x=pos.x+fx, y=pos.y+1, z=pos.z+fz}}, {{name=fl[math.random(1,4)]}})
    end
    fill_cylinder(pos, 0, 1, 0, 1, math.ceil({s}*4), "default:tree")
    fill_sphere(pos, 0, math.ceil({s}*4)+1, 0, math.ceil({s}*3), "default:leaves")
    for x=-w, w do
        minetest.set_node({{x=pos.x+x, y=pos.y+1, z=pos.z-w}}, {{name="default:fence_wood"}})
        minetest.set_node({{x=pos.x+x, y=pos.y+1, z=pos.z+w}}, {{name="default:fence_wood"}})
    end
    for z=-w, w do
        minetest.set_node({{x=pos.x-w, y=pos.y+1, z=pos.z+z}}, {{name="default:fence_wood"}})
        minetest.set_node({{x=pos.x+w, y=pos.y+1, z=pos.z+z}}, {{name="default:fence_wood"}})
    end
end"""
    elif btype == "temple":
        tw = int(8*s); th = int(6*s)
        return f"""local function build_structure(pos)
    local w = {tw} local h = {th}
    for step=0, 3 do local sw = w - step*2
        fill_box(pos, -sw, step, -sw, sw, step, sw, B)
    end
    for _, c in ipairs({{{{-w+2,-w+2}},{{w-2,-w+2}},{{-w+2,w-2}},{{w-2,w-2}}}}) do
        fill_box(pos, c[1], 4, c[2], c[1], h, c[2], B)
    end
    fill_box(pos, -w+1, h+1, -w+1, w-1, h+1, w-1, B)
    fill_box(pos, -w, h+2, -w, w, h+2, w, B)
    minetest.set_node({{x=pos.x, y=pos.y+5, z=pos.z}}, {{name="my_first_mod:brick_glow"}})
end"""
    elif btype == "statue":
        sh = int(10*s)
        return f"""local function build_structure(pos)
    local h = {sh}
    fill_box(pos, -2, 0, -2, 2, 2, 2, B)
    fill_box(pos, -1, 3, -1, 1, h-2, 1, B)
    fill_sphere(pos, 0, h-1, 0, 2, B)
    fill_box(pos, -3, math.floor(h/2), 0, -2, math.floor(h/2)+2, 0, B)
    fill_box(pos, 2, math.floor(h/2), 0, 3, math.floor(h/2)+2, 0, B)
end"""
    elif btype == "fountain":
        fr = int(4*s)
        return f"""local function build_structure(pos)
    local r = {fr}
    fill_cylinder(pos, 0, 1, 0, r, 1, B)
    fill_cylinder(pos, 0, 1, 0, r-1, 1, B)
    fill_cylinder(pos, 0, 2, 0, 1, math.ceil({s}*3), B)
    fill_cylinder(pos, 0, math.ceil({s}*3)+2, 0, 2, 1, B)
end"""
    elif btype == "lighthouse":
        lh = int(15*s); lr = max(2, int(3*s))
        return f"""local function build_structure(pos)
    local h = {lh} local r = {lr}
    for y=0, h do
        local b = (math.floor(y/3)%2==0) and B or "default:white"
        fill_cylinder(pos, 0, y, 0, r, 1, b)
    end
    fill_cylinder(pos, 0, h+1, 0, r-1, 2, "default:glass")
    minetest.set_node({{x=pos.x, y=pos.y+h+2, z=pos.z}}, {{name="my_first_mod:brick_glow"}})
end"""
    elif btype == "wall":
        wl = int(20*s); wh = int(4*s)
        return f"""local function build_structure(pos)
    local length = {wl} local h = {wh}
    fill_box(pos, 0, 1, -1, length, h+1, 1, B)
    for x=0, length, 2 do
        minetest.set_node({{x=pos.x+x, y=pos.y+h+1, z=pos.z}}, {{name=B}})
    end
end"""
    elif btype == "tree":
        th2 = int(8*s); tr2 = int(4*s)
        return f"""local function build_structure(pos)
    fill_cylinder(pos, 0, 1, 0, 1, {th2}, "default:tree")
    fill_sphere(pos, 0, {th2}, 0, {tr2}, "default:leaves")
    fill_sphere(pos, 0, {th2}+{tr2}, 0, {tr2}-1, "default:leaves")
end"""
    elif btype in ("spaceship","rocket"):
        return f"""local function build_structure(pos)
    local r = math.ceil({s}*4)
    fill_cylinder(pos, 0, 1, 0, 2, math.ceil({s}*8), B)
    fill_sphere(pos, 0, math.ceil({s}*8)+1, 0, 2, B)
    fill_box(pos, -r, 3, -1, r, 4, 1, B)
    fill_cylinder(pos, -2, 1, 0, 1, 2, "default:furnace_active")
    fill_cylinder(pos, 2, 1, 0, 1, 2, "default:furnace_active")
    fill_box(pos, -1, math.ceil({s}*6), 0, 1, math.ceil({s}*6), 0, "default:glass")
end"""
    elif btype == "mushroom":
        mh = int(5*s); mr = max(2, int(3*s))
        return f"""local function build_structure(pos)
    fill_cylinder(pos, 0, 1, 0, 1, {mh}, "default:white")
    fill_sphere(pos, 0, {mh}, 0, {mr}, B)
    fill_box(pos, -{mr}, 0, -{mr}, {mr}, 0, {mr}, "air")
end"""
    elif btype == "heart":
        scale = max(1, int(s*2))
        return f"""local function build_structure(pos)
    local s = {scale}
    local pattern = {{".##...##.","#########","#########","#########",".#######.","..#####..","...###...","....#...."}}
    for row=1, #pattern do
        local line = pattern[row]
        for col=1, #line do
            if line:sub(col,col)=="#" then
                for dx=0,s-1 do for dy=0,s-1 do
                    minetest.set_node({{x=pos.x+(col-1)*s+dx, y=pos.y+(#pattern-row)*s+dy, z=pos.z}}, {{name=B}})
                end end
            end
        end
    end
end"""
    elif btype == "sphere":
        sr = max(3, int(6*s))
        return f"""local function build_structure(pos)
    fill_sphere(pos, 0, {sr}, 0, {sr}, B)
end"""
    elif btype == "spiral":
        sph = int(20*s)
        return f"""local function build_structure(pos)
    local h = {sph}
    for y=0, h do
        local angle = y*0.5
        local r = math.max(2, math.floor(5-y*2/h))
        local x = math.floor(math.cos(angle)*r)
        local z = math.floor(math.sin(angle)*r)
        minetest.set_node({{x=pos.x+x, y=pos.y+y, z=pos.z+z}}, {{name=B}})
    end
end"""
    elif btype == "shanghai":
        return f"""local function build_structure(pos)
    fill_cylinder(pos, 30, 1, 0, 2, math.ceil({s}*30), B)
    fill_sphere(pos, 30, math.ceil({s}*15), 0, math.ceil({s}*4), B)
    fill_sphere(pos, 30, math.ceil({s}*25), 0, math.ceil({s}*3), B)
    for y=0, math.ceil({s}*50) do
        local r = math.max(2, math.floor(5-y*3/math.ceil({s}*50)))
        for x=-r, r do for z=-r, r do
            if math.abs(x)==r or math.abs(z)==r then
                minetest.set_node({{x=pos.x+38+x, y=pos.y+y, z=pos.z+z}}, {{name=B}})
            end
        end end
    end
    for sec=0, 5 do
        local r = math.max(1, 4-sec) local y0 = sec*math.ceil({s}*7)
        fill_box(pos, 32-r, y0, -r, 32+r, y0+math.ceil({s}*6), r, B)
    end
end"""
    elif btype == "village":
        return f"""local function build_structure(pos)
    local houses = math.max(3, math.ceil({s}*5))
    for i=1, houses do
        local angle = (i/houses)*math.pi*2
        local dist = math.ceil({s}*12)
        local hx = math.floor(math.cos(angle)*dist) local hz = math.floor(math.sin(angle)*dist)
        local colors = {{"default:wood","default:brick","default:sandstone","default:stone"}}
        local hb = colors[((i-1)%#colors)+1]
        local h = math.ceil({s}*4) local w = math.ceil({s}*3)
        fill_shell(pos, hx-w, 1, hz-w, hx+w, h+1, hz+w, hb)
        fill_box(pos, hx-w-1, h+2, hz-w-1, hx+w+1, h+2, hz+w+1, "default:wood")
        fill_box(pos, hx-1, 1, hz-w, hx+1, 3, hz-w, "air")
    end
end"""
    else:
        h2 = int(4*s); w2 = int(5*s)
        return f"""local function build_structure(pos)
    local h = {h2} local w = {w2}
    fill_shell(pos, -w, 0, -w, w, h, w, B)
    fill_box(pos, -w+1, 0, -w+1, w-1, 0, w-1, B)
    fill_box(pos, -1, 0, -w, 1, 2, -w, "air")
    fill_box(pos, -w-1, h+1, -w-1, w+1, h+1, w+1, "default:wood")
    minetest.set_node({{x=pos.x, y=pos.y+h-1, z=pos.z}}, {{name="my_first_mod:brick_glow"}})
end"""

# ============================================================
# 安装 mod
# ============================================================

def install_mod(lua_code):
    mods_dir = get_minetest_dir() / "mods"
    mods_dir.mkdir(parents=True, exist_ok=True)
    mod_dir = mods_dir / "nl_builder"
    mod_dir.mkdir(parents=True, exist_ok=True)
    (mod_dir / "mod.conf").write_text(
        "name = nl_builder\ndescription = 自然语言生成的建筑\ndepends = default\n", encoding="utf-8")
    (mod_dir / "init.lua").write_text(lua_code, encoding="utf-8")
    return str(mod_dir)

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

# ============================================================
# 启动 Luanti
# ============================================================

def list_worlds():
    """列出所有可用世界"""
    mt_dir = get_minetest_dir()
    worlds_dir = mt_dir / "worlds"
    worlds = []
    if worlds_dir.exists():
        for d in sorted(worlds_dir.iterdir()):
            if d.is_dir() and (d / "world.mt").exists():
                # 读取 world_name
                name = d.name
                try:
                    content = (d / "world.mt").read_text()
                    for line in content.split("\n"):
                        if line.strip().startswith("world_name"):
                            name = line.split("=", 1)[1].strip()
                            break
                except:
                    pass
                worlds.append({"name": name, "dir": d.name, "path": str(d)})
    return worlds

def enable_mod_in_world(world_dir=None):
    """在世界配置中启用 nl_builder mod，返回世界路径"""
    mt_dir = get_minetest_dir()
    worlds_dir = mt_dir / "worlds"

    # 如果没指定世界，找第一个可用的
    if world_dir is None:
        if worlds_dir.exists():
            for d in sorted(worlds_dir.iterdir()):
                if d.is_dir() and (d / "world.mt").exists():
                    world_dir = d
                    break
        if world_dir is None:
            return None
    else:
        world_dir = Path(world_dir)
        if not world_dir.exists():
            return None

    world_mt = world_dir / "world.mt"
    if not world_mt.exists():
        return None

    # 读取现有配置
    content = world_mt.read_text(encoding="utf-8")

    # 检查是否已有 load_mod_nl_builder
    if "load_mod_nl_builder" in content:
        # 替换为 true
        content = re.sub(r'load_mod_nl_builder\s*=\s*\w+',
                        'load_mod_nl_builder = true', content)
    else:
        # 追加
        content = content.rstrip() + "\nload_mod_nl_builder = true\n"

    world_mt.write_text(content, encoding="utf-8")
    return str(world_dir)

def launch_luanti(world_path=None):
    """启动 Luanti/Minetest 游戏，可选直接进入指定世界"""
    import subprocess

    system = platform.system()
    candidates = []

    # 构建启动参数
    extra_args = []
    if world_path:
        extra_args = ["--world", world_path, "--go"]

    if system == "Darwin":
        for app_name in ["luanti", "minetest"]:
            app_path = f"/Applications/{app_name}.app"
            if os.path.exists(app_path):
                if extra_args:
                    candidates.append(("open", [app_path, "--args"] + extra_args))
                else:
                    candidates.append(("open", [app_path]))
        for exe in ["/Applications/luanti.app/Contents/MacOS/luanti",
                    "/Applications/minetest.app/Contents/MacOS/minetest"]:
            if os.path.exists(exe):
                candidates.append((exe, extra_args))
    elif system == "Linux":
        for exe in ["luanti", "minetest"]:
            result = subprocess.run(["which", exe], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                candidates.append((result.stdout.strip(), extra_args))
        candidates.append(("flatpak", ["run", "net.minetest.Minetest"] + extra_args))
    elif system == "Windows":
        for base in [os.environ.get("PROGRAMFILES", "C:\\Program Files"),
                      os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)")]:
            for name in ["Luanti", "Minetest"]:
                exe = os.path.join(base, name, f"{name}.exe")
                if os.path.exists(exe):
                    candidates.append((exe, extra_args))

    if not candidates:
        return {"error": f"未找到 Luanti/Minetest，请确认已安装。系统: {system}"}

    try:
        exe, args = candidates[0]
        cmd = [exe] + (args if isinstance(args, list) else list(args))
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return {"success": True, "message": f"Luanti 已启动: {exe}"}
    except Exception as e:
        return {"error": f"启动失败: {str(e)}"}

# ============================================================
# Web 服务器
# ============================================================

HTML_PAGE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Luanti 自然语言建筑生成器</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; background:#1a1a2e; color:#e0e0e0; min-height:100vh; font-size:15px; }
.container { max-width:960px; margin:0 auto; padding:24px; }
h1 { text-align:center; font-size:26px; margin:10px 0 6px; color:#50fa7b; }
.subtitle { text-align:center; color:#888; font-size:14px; margin-bottom:20px; }
.card { background:#16213e; border-radius:12px; padding:24px; margin-bottom:18px; box-shadow:0 4px 6px rgba(0,0,0,0.3); }
label { display:block; font-size:15px; color:#aaa; margin-bottom:8px; }
input[type="text"] { width:100%; padding:14px; font-size:17px; border:2px solid #0f3460; border-radius:8px; background:#1a1a2e; color:#fff; }
input[type="text"]:focus { outline:none; border-color:#50fa7b; }
.examples { margin-top:10px; }
.example-btn { display:inline-block; background:#0f3460; color:#8be9fd; padding:6px 12px; border-radius:6px; font-size:13px; margin:4px; cursor:pointer; border:1px solid #1a4080; transition:0.2s; }
.example-btn:hover { background:#1a4080; }
.btn-row { display:flex; gap:12px; margin-top:14px; flex-wrap:wrap; }
button { padding:12px 24px; font-size:15px; border:none; border-radius:8px; cursor:pointer; font-weight:600; transition:0.2s; }
.btn-parse { background:#0f3460; color:#8be9fd; }
.btn-parse:hover { background:#1a4080; }
.btn-gen { background:#5046e5; color:#fff; }
.btn-gen:hover { background:#6056f5; }
.btn-install { background:#50fa7b; color:#1a1a2e; }
.btn-install:hover { background:#60ffa0; }
.btn-all { background:#ff79c6; color:#fff; }
.btn-all:hover { background:#ff99d6; }
.btn-preview { background:#f1fa8c; color:#1a1a2e; }
.btn-preview:hover { background:#ffffaa; }
.btn-launch { background:#50fa7b; color:#1a1a2e; border:2px solid #50fa7b; }
.btn-launch:hover { background:#60ffa0; box-shadow:0 0 12px #50fa7b; }
.btn-ai { background:#bd93f9; color:#1a1a2e; }
.btn-ai:hover { background:#caa0ff; }
.btn-ai-all { background:#ff6b6b; color:#fff; }
.btn-ai-all:hover { background:#ff8585; box-shadow:0 0 12px #ff6b6b; }
.ai-settings { background:#0d1117; border:1px solid #333; border-radius:8px; padding:14px; margin-top:12px; }
.ai-settings label { font-size:13px; color:#6272a4; margin-bottom:4px; }
.ai-settings input { width:100%; padding:8px; background:#1a1a2e; color:#e0e0e0; border:1px solid #0f3460; border-radius:6px; font-size:14px; margin-bottom:8px; }
.ai-settings input:focus { outline:none; border-color:#50fa7b; }
.ai-row { display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; }
@media(max-width:600px) { .ai-row { grid-template-columns:1fr; } }
.ai-loading { display:none; text-align:center; padding:20px; }
.ai-loading.show { display:block; }
.spinner { display:inline-block; width:32px; height:32px; border:3px solid #333; border-top:3px solid #50fa7b; border-radius:50%; animation:spin 1s linear infinite; }
@keyframes spin { 0%{transform:rotate(0)} 100%{transform:rotate(360deg)} }
.preview-container { position:relative; background:#0d1117; border-radius:8px; border:1px solid #333; overflow:hidden; }
.preview-canvas { display:block; margin:0 auto; cursor:grab; }
.preview-canvas:active { cursor:grabbing; }
.preview-controls { position:absolute; top:8px; right:8px; display:flex; gap:6px; }
.preview-controls button { padding:5px 12px; font-size:13px; background:#0f3460; color:#8be9fd; border-radius:4px; }
.result { background:#0d1117; border-radius:8px; padding:14px; font-family:monospace; font-size:14px; white-space:pre-wrap; color:#8be9fd; min-height:50px; }
.code-box { background:#0d1117; border-radius:8px; padding:14px; font-family:"Courier New",monospace; font-size:13px; white-space:pre; overflow:auto; max-height:400px; color:#c0c0c0; border:1px solid #333; }
.status { padding:10px 18px; border-radius:8px; margin-top:10px; font-size:15px; }
.status-ok { background:#1a3a1a; color:#50fa7b; }
.status-warn { background:#3a3a1a; color:#f1fa8c; }
.status-err { background:#3a1a1a; color:#ff5555; }
.path-info { font-size:13px; color:#6272a4; margin-top:8px; word-break:break-all; }
.grid { display:grid; grid-template-columns:1fr 1fr; gap:18px; }
@media(max-width:600px) { .grid { grid-template-columns:1fr; } .btn-row { flex-direction:column; } }
table { width:100%; border-collapse:collapse; font-size:14px; }
th,td { padding:8px 12px; border-bottom:1px solid #333; text-align:left; }
th { color:#50fa7b; }
td { color:#aaa; }
</style>
</head>
<body>
<div class="container">
<h1>🏗️ Luanti 自然语言建筑生成器</h1>
<p class="subtitle">输入自然语言 → 自动解析 → 生成 Lua mod → 安装到 Luanti</p>

<div class="card">
<label>描述你想要的建筑：</label>
<input type="text" id="input" value="建一个红色的城堡，有塔楼" placeholder="例如：建造一座大型金字塔">
<div class="examples">
<span style="color:#666;font-size:12px">示例：</span>
<span class="example-btn" onclick="setInput(this.textContent)">建一个红色的城堡，有塔楼</span>
<span class="example-btn" onclick="setInput(this.textContent)">建造一座大型金字塔</span>
<span class="example-btn" onclick="setInput(this.textContent)">做一个发光的灯塔</span>
<span class="example-btn" onclick="setInput(this.textContent)">建一座桥</span>
<span class="example-btn" onclick="setInput(this.textContent)">建造一个花园</span>
<span class="example-btn" onclick="setInput(this.textContent)">做一个爱心</span>
<span class="example-btn" onclick="setInput(this.textContent)">建一座神殿</span>
<span class="example-btn" onclick="setInput(this.textContent)">建造一棵巨大的树</span>
<span class="example-btn" onclick="setInput(this.textContent)">做一个飞船</span>
<span class="example-btn" onclick="setInput(this.textContent)">建一个村庄</span>
</div>
<div class="btn-row">
<button class="btn-parse" onclick="doParse()">🔍 解析</button>
<button class="btn-gen" onclick="doGen()">📋 生成 Lua</button>
<button class="btn-install" onclick="doInstall()">💾 安装</button>
<button class="btn-all" onclick="doAll()">🚀 生成并安装</button>
<button class="btn-preview" onclick="doPreview()">👁️ 预览</button>
<button class="btn-launch" onclick="doJoin()">🎮 一键加入游戏</button>
<button class="btn-ai" onclick="doAIPreview()">🤖 AI 预览</button>
<button class="btn-ai-all" onclick="doAIGenerate()">🤖 AI 生成并加入</button>
</div>
<div style="margin-top:8px; display:flex; align-items:center; gap:8px;">
<label style="font-size:13px; color:#6272a4; white-space:nowrap;">选择世界:</label>
<select id="worldSelect" style="flex:1; padding:6px; background:#1a1a2e; color:#e0e0e0; border:1px solid #0f3460; border-radius:6px; font-size:13px;">
<option value="">自动选择</option>
</select>
</div>

<!-- AI 大模型设置 -->
<div class="ai-settings">
<label>🤖 AI 大模型设置 (用于复杂建筑，如"比萨斜塔""埃菲尔铁塔")</label>
<div style="margin-bottom:10px;">
<label>快速选择</label>
<select id="aiProvider" onchange="switchProvider()" style="width:100%; padding:8px; background:#1a1a2e; color:#e0e0e0; border:1px solid #0f3460; border-radius:6px; font-size:14px;">
<optgroup label="─ 国内可用 ─">
<option value="deepseek">DeepSeek (推荐, 便宜)</option>
<option value="zhipu">智谱 GLM (免费额度)</option>
<option value="qwen">通义千问 阿里 (免费额度)</option>
<option value="moonshot">Moonshot Kimi (长上下文)</option>
<option value="baichuan">百川 Baichuan</option>
<option value="minimax">MiniMax</option>
<option value="yi">零一万物 Yi</option>
<option value="stepfun">阶跃星辰 Step</option>
<option value="sensetime">商汤 SenseNova</option>
<option value="iflytek">讯飞星火 iFlyTek</option>
<option value="hunyuan">腾讯混元</option>
<option value="ernie">百度文心 ERNIE</option>
<option value="volcengine">火山引擎 豆包</option>
<option value="siliconflow">硅基流动 SiliconFlow (聚合, 免费)</option>
<option value="openrouter_cn">OpenRouter (国内代理)</option>
</optgroup>
<optgroup label="─ 国际 ─">
<option value="openai">OpenAI GPT (需翻墙)</option>
<option value="anthropic">Anthropic Claude (需翻墙)</option>
<option value="google">Google Gemini (需翻墙)</option>
<option value="openrouter">OpenRouter (聚合, 需翻墙)</option>
<option value="groq">Groq (超快, 需翻墙)</option>
<option value="together">Together AI (需翻墙)</option>
<option value="mistral">Mistral AI (需翻墙)</option>
<option value="cohere">Cohere (需翻墙)</option>
<option value="perplexity">Perplexity (需翻墙)</option>
<option value="anyscale">Anyscale (需翻墙)</option>
<option value="fireworks">Fireworks AI (需翻墙)</option>
<option value="lepton">Lepton AI (需翻墙)</option>
<option value="novita">Novita AI (需翻墙)</option>
</optgroup>
<optgroup label="─ 其他 ─">
<option value="ollama">Ollama 本地模型 (免费, 需安装)</option>
<option value="lmstudio">LM Studio 本地 (免费, 需安装)</option>
<option value="custom">自定义</option>
</optgroup>
</select>
</div>
<div class="ai-row">
<div>
<label>API Key</label>
<input type="text" id="apiKey" placeholder="sk-..." oninput="saveAIConfig()">
</div>
<div>
<label>Base URL</label>
<input type="text" id="baseUrl" value="https://api.deepseek.com/v1" oninput="saveAIConfig()">
</div>
<div>
<label>模型</label>
<input type="text" id="modelName" value="deepseek-chat" oninput="saveAIConfig()">
</div>
</div>
<p style="font-size:12px; color:#6272a4; margin-top:6px;">API Key 保存在浏览器本地，不会上传。</p>
</div>

<!-- AI 加载动画 -->
<div class="ai-loading" id="aiLoading">
<div class="spinner"></div>
<p style="margin-top:10px; color:#6272a4;">🤖 AI 正在生成建筑，请稍候...</p>
</div>
</div>
<div class="card">
<label>解析结果：</label>
<div class="result" id="result">等待输入...</div>
</div>
<div class="card">
<label>状态：</label>
<div id="status" class="status status-warn">就绪</div>
<div class="path-info" id="pathInfo"></div>
</div>
</div>

<div class="card">
<label>生成的 Lua 代码：</label>
<div class="code-box" id="code">点击「生成 Lua」按钮查看代码</div>
</div>

<div class="card">
<label>3D 预览 (拖拽旋转)：</label>
<div class="preview-container">
<canvas id="previewCanvas" class="preview-canvas" width="600" height="400"></canvas>
<div class="preview-controls">
<button onclick="zoomPreview(1.2)">➕</button>
<button onclick="zoomPreview(0.8)">➖</button>
<button onclick="resetPreview()">🔄</button>
</div>
</div>
</div>

<div class="card">
<label>支持的建筑类型：</label>
<table>
<tr><th>类型</th><th>关键词</th><th>类型</th><th>关键词</th></tr>
<tr><td>🏰 城堡</td><td>castle</td><td>🏠 房子</td><td>house</td></tr>
<tr><td>🗼 塔</td><td>tower</td><td>🔺 金字塔</td><td>pyramid</td></tr>
<tr><td>🌉 桥</td><td>bridge</td><td>🌷 花园</td><td>garden</td></tr>
<tr><td>⛩️ 神殿</td><td>temple</td><td>🗿 雕像</td><td>statue</td></tr>
<tr><td>⛲ 喷泉</td><td>fountain</td><td>💡 灯塔</td><td>lighthouse</td></tr>
<tr><td>🧱 城墙</td><td>wall</td><td>🌳 树</td><td>tree</td></tr>
<tr><td>🚀 飞船</td><td>spaceship</td><td>🍄 蘑菇</td><td>mushroom</td></tr>
<tr><td>❤️ 爱心</td><td>heart</td><td>🔮 球体</td><td>sphere</td></tr>
<tr><td>🌀 螺旋塔</td><td>spiral</td><td>🏘️ 村庄</td><td>village</td></tr>
</table>
</div>
</div>

<script>
function setInput(text) { document.getElementById('input').value = text; }
function setStatus(msg, cls) {
    const s = document.getElementById('status');
    s.textContent = msg;
    s.className = 'status ' + (cls || 'status-ok');
}
function fetchAPI(action, params) {
    const input = document.getElementById('input').value;
    const url = '/api?action=' + action + '&input=' + encodeURIComponent(input);
    return fetch(url).then(r => r.json());
}
function doParse() {
    fetchAPI('parse').then(data => {
        if(data.error) { setStatus(data.error, 'status-err'); if(data.raw) { document.getElementById('code').textContent = 'AI 返回内容:\\n' + data.raw; } return; }
        const p = data.params;
        const sizes = ['小','中','大','巨大'];
        const text = `类型: ${p.type || '未知'}\\n颜色: ${p.color || '默认'}\\n尺寸: ${sizes[p.size]}\\n材质: ${p.material || '默认'}\\n特征: ${p.features && p.features.length ? p.features.join(', ') : '无'}`;
        document.getElementById('result').textContent = text;
        setStatus('✅ 解析完成', 'status-ok');
    });
}
function doGen() {
    fetchAPI('generate').then(data => {
        if(data.error) { setStatus(data.error, 'status-err'); if(data.raw) { document.getElementById('code').textContent = 'AI 返回内容:\\n' + data.raw; } return; }
        document.getElementById('code').textContent = data.lua;
        setStatus('✅ Lua 代码已生成', 'status-ok');
    });
}
function doInstall() {
    fetchAPI('install').then(data => {
        if(data.error) { setStatus(data.error, 'status-err'); if(data.raw) { document.getElementById('code').textContent = 'AI 返回内容:\\n' + data.raw; } return; }
        document.getElementById('code').textContent = data.lua;
        document.getElementById('pathInfo').textContent = '安装路径: ' + data.path;
        setStatus('✅ 已安装到 Luanti mods 目录！进入游戏输入 /build 生成建筑', 'status-ok');
    });
}
function doAll() {
    doParse();
    doInstall();
    doPreview();
}
function doLaunch() {
    setStatus('⏳ 正在启动 Luanti...', 'status-warn');
    fetch('/api?action=launch').then(r => r.json()).then(data => {
        if(data.error) { setStatus(data.error, 'status-err'); if(data.raw) { document.getElementById('code').textContent = 'AI 返回内容:\\n' + data.raw; } return; }
        setStatus('✅ Luanti 已启动！进入游戏后输入 /build 生成建筑', 'status-ok');
    }).catch(() => {
        setStatus('❌ 启动失败，请手动打开 Luanti', 'status-err');
    });
}
function doJoin() {
    const world = document.getElementById('worldSelect').value;
    const input = document.getElementById('input').value;
    setStatus('⏳ 正在安装 mod + 启用世界 + 启动游戏...', 'status-warn');
    const url = '/api?action=join&input=' + encodeURIComponent(input) + (world ? '&world=' + encodeURIComponent(world) : '');
    fetch(url).then(r => r.json()).then(data => {
        if(data.error) { setStatus(data.error, 'status-err'); if(data.raw) { document.getElementById('code').textContent = 'AI 返回内容:\\n' + data.raw; } return; }
        document.getElementById('code').textContent = data.lua || '';
        document.getElementById('pathInfo').textContent = 'Mod: ' + (data.mod_path||'') + ' | 世界: ' + (data.world_path||'');
        const lr = data.launch || {};
        if(lr.error) {
            setStatus('⚠️ Mod已安装但启动失败: ' + lr.error + '。请手动启动', 'status-warn');
        } else {
            setStatus('✅ 一键完成！游戏已启动，进入后输入 /build 生成建筑', 'status-ok');
        }
    }).catch(() => {
        setStatus('❌ 请求失败', 'status-err');
    });
}

// ===== AI 大模型功能 =====
function saveAIConfig() {
    localStorage.setItem('ai_api_key', document.getElementById('apiKey').value);
    localStorage.setItem('ai_base_url', document.getElementById('baseUrl').value);
    localStorage.setItem('ai_model', document.getElementById('modelName').value);
    localStorage.setItem('ai_provider', document.getElementById('aiProvider').value);
}
function switchProvider() {
    const p = document.getElementById('aiProvider').value;
    const configs = {
        // 国内
        'deepseek':      {url:'https://api.deepseek.com/v1', model:'deepseek-chat'},
        'zhipu':         {url:'https://open.bigmodel.cn/api/paas/v4', model:'glm-4-flash'},
        'qwen':          {url:'https://dashscope.aliyuncs.com/compatible-mode/v1', model:'qwen-turbo'},
        'moonshot':      {url:'https://api.moonshot.cn/v1', model:'moonshot-v1-8k'},
        'baichuan':      {url:'https://api.baichuan-ai.com/v1', model:'Baichuan4'},
        'minimax':       {url:'https://api.minimax.chat/v1', model:'abab6.5-chat'},
        'yi':            {url:'https://api.lingyiwanwu.com/v1', model:'yi-large'},
        'stepfun':       {url:'https://api.stepfun.com/v1', model:'step-1-8k'},
        'sensetime':     {url:'https://api.sensenova.cn/compatible-mode/v1', model:'SenseChat-5'},
        'iflytek':       {url:'https://spark-api-open.xf-yun.com/v1', model:'4.0Ultra'},
        'hunyuan':       {url:'https://api.hunyuan.cloud.tencent.com/v1', model:'hunyuan-pro'},
        'ernie':         {url:'https://qianfan.baidubce.com/v2', model:'ernie-4.0-8k-latest'},
        'volcengine':    {url:'https://ark.cn-beijing.volces.com/api/v3', model:'doubao-pro-4k'},
        'siliconflow':   {url:'https://api.siliconflow.cn/v1', model:'Qwen/Qwen2.5-7B-Instruct'},
        'openrouter_cn': {url:'https://openrouter.ai/api/v1', model:'deepseek/deepseek-chat'},
        // 国际
        'openai':        {url:'https://api.openai.com/v1', model:'gpt-4o-mini'},
        'anthropic':     {url:'https://api.anthropic.com/v1', model:'claude-3-5-haiku-20241022'},
        'google':        {url:'https://generativelanguage.googleapis.com/v1beta/openai', model:'gemini-1.5-flash'},
        'openrouter':    {url:'https://openrouter.ai/api/v1', model:'openai/gpt-4o-mini'},
        'groq':          {url:'https://api.groq.com/openai/v1', model:'llama-3.3-70b-versatile'},
        'together':      {url:'https://api.together.xyz/v1', model:'meta-llama/Llama-3.3-70B-Instruct-Turbo'},
        'mistral':       {url:'https://api.mistral.ai/v1', model:'mistral-small-latest'},
        'cohere':        {url:'https://api.cohere.ai/v1', model:'command-r-plus'},
        'perplexity':    {url:'https://api.perplexity.ai', model:'llama-3.1-8b-instruct'},
        'anyscale':      {url:'https://api.endpoints.anyscale.com/v1', model:'meta-llama/Llama-3.1-8B-Instruct'},
        'fireworks':     {url:'https://api.fireworks.ai/inference/v1', model:'accounts/fireworks/models/llama-v3p1-8b-instruct'},
        'lepton':        {url:'https://llama3-1-8b.lepton.run/api/v1', model:'llama3.1-8b'},
        'novita':        {url:'https://api.novita.ai/v3/openai', model:'meta-llama/llama-3.1-8b-instruct'},
        // 本地
        'ollama':        {url:'http://localhost:11434/v1', model:'llama3.2'},
        'lmstudio':      {url:'http://localhost:1234/v1', model:'local-model'},
        'custom':        {url:'', model:''},
    };
    const c = configs[p];
    if (c) {
        document.getElementById('baseUrl').value = c.url;
        document.getElementById('modelName').value = c.model;
        saveAIConfig();
    }
}
function loadAIConfig() {
    document.getElementById('apiKey').value = localStorage.getItem('ai_api_key') || '';
    document.getElementById('baseUrl').value = localStorage.getItem('ai_base_url') || 'https://api.deepseek.com/v1';
    document.getElementById('modelName').value = localStorage.getItem('ai_model') || 'deepseek-chat';
    document.getElementById('aiProvider').value = localStorage.getItem('ai_provider') || 'deepseek';
}
function getAIUrl(action) {
    const input = document.getElementById('input').value;
    const key = encodeURIComponent(document.getElementById('apiKey').value);
    const url_val = encodeURIComponent(document.getElementById('baseUrl').value);
    const model = encodeURIComponent(document.getElementById('modelName').value);
    const world = document.getElementById('worldSelect').value;
    let url = '/api?action=' + action + '&input=' + encodeURIComponent(input) +
              '&api_key=' + key + '&base_url=' + url_val + '&model=' + model;
    if (world) url += '&world=' + encodeURIComponent(world);
    return url;
}
function showAILoading(show) {
    document.getElementById('aiLoading').classList.toggle('show', show);
}
function doAIPreview() {
    const key = document.getElementById('apiKey').value;
    if (!key) { setStatus('⚠️ 请先填写 API Key', 'status-warn'); return; }
    showAILoading(true);
    setStatus('🤖 AI 正在生成...', 'status-warn');
    fetch(getAIUrl('ai_preview')).then(r => r.json()).then(data => {
        showAILoading(false);
        if(data.error) { setStatus(data.error, 'status-err'); if(data.raw) { document.getElementById('code').textContent = 'AI 返回内容:\\n' + data.raw; } return; }
        previewBlocks = data.blocks || [];
        renderPreview();
        setStatus('✅ AI 预览已生成 (' + (data.count||0) + ' 个方块)', 'status-ok');
    }).catch(() => {
        showAILoading(false);
        setStatus('❌ AI 请求失败', 'status-err');
    });
}
function doAIGenerate() {
    const key = document.getElementById('apiKey').value;
    if (!key) { setStatus('⚠️ 请先填写 API Key', 'status-warn'); return; }
    showAILoading(true);
    setStatus('🤖 AI 生成中 + 安装 + 启动游戏...', 'status-warn');
    fetch(getAIUrl('ai_install')).then(r => r.json()).then(data => {
        showAILoading(false);
        if(data.error) { setStatus(data.error, 'status-err'); if(data.raw) { document.getElementById('code').textContent = 'AI 返回内容:\\n' + data.raw; } return; }
        document.getElementById('code').textContent = data.lua || '';
        previewBlocks = data.blocks || [];
        renderPreview();
        document.getElementById('pathInfo').textContent = 'Mod: ' + (data.mod_path||'') + ' | 方块: ' + (data.count||0);
        const lr = data.launch || {};
        if(lr.error) {
            setStatus('⚠️ Mod已安装但启动失败: ' + lr.error, 'status-warn');
        } else {
            setStatus('✅ AI 建筑已生成并安装！(' + (data.count||0) + ' 方块) 进入游戏输入 /build', 'status-ok');
        }
    }).catch(() => {
        showAILoading(false);
        setStatus('❌ AI 请求失败', 'status-err');
    });
}

// ===== 3D 预览 =====
let previewBlocks = [];
let previewState = { angleX: -0.5, angleY: 0.5, zoom: 1.0, dragging: false, lastX: 0, lastY: 0 };

function doPreview() {
    fetchAPI('preview').then(data => {
        if(data.error) { setStatus(data.error, 'status-err'); if(data.raw) { document.getElementById('code').textContent = 'AI 返回内容:\\n' + data.raw; } return; }
        previewBlocks = data.blocks || [];
        renderPreview();
        setStatus('✅ 3D 预览已生成 (' + previewBlocks.length + ' 个方块)', 'status-ok');
    });
}

function zoomPreview(factor) {
    previewState.zoom *= factor;
    previewState.zoom = Math.max(0.3, Math.min(3.0, previewState.zoom));
    renderPreview();
}

function resetPreview() {
    previewState = { angleX: -0.5, angleY: 0.5, zoom: 1.0, dragging: false, lastX: 0, lastY: 0 };
    renderPreview();
}

function renderPreview() {
    const canvas = document.getElementById('previewCanvas');
    const ctx = canvas.getContext('2d');
    const w = canvas.width, h = canvas.height;
    ctx.fillStyle = '#0d1117';
    ctx.fillRect(0, 0, w, h);

    if (previewBlocks.length === 0) {
        ctx.fillStyle = '#6272a4';
        ctx.font = '14px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('点击「👁️ 预览」按钮查看 3D 效果', w/2, h/2);
        return;
    }

    // 找到边界
    let minX=Infinity, maxX=-Infinity, minY=Infinity, maxY=-Infinity, minZ=Infinity, maxZ=-Infinity;
    for (const b of previewBlocks) {
        minX = Math.min(minX, b.x); maxX = Math.max(maxX, b.x);
        minY = Math.min(minY, b.y); maxY = Math.max(maxY, b.y);
        minZ = Math.min(minZ, b.z); maxZ = Math.max(maxZ, b.z);
    }
    const cx = (minX + maxX) / 2;
    const cy = (minY + maxY) / 2;
    const cz = (minZ + maxZ) / 2;
    const range = Math.max(maxX-minX, maxY-minY, maxZ-minZ) + 2;
    const scale = Math.min(w, h) / range * 0.8 * previewState.zoom;

    // 等距投影变换
    function project(x, y, z) {
        const dx = (x - cx) * scale;
        const dy = (y - cy) * scale;
        const dz = (z - cz) * scale;
        // 先 Y 轴旋转
        const cosY = Math.cos(previewState.angleY);
        const sinY = Math.sin(previewState.angleY);
        const rx = dx * cosY - dz * sinY;
        const rz = dx * sinY + dz * cosY;
        // 再 X 轴旋转
        const cosX = Math.cos(previewState.angleX);
        const sinX = Math.sin(previewState.angleX);
        const ry = dy * cosX - rz * sinX;
        const rz2 = dy * sinX + rz * cosX;
        // 投影
        return {
            sx: w/2 + rx,
            sy: h/2 + ry,
            depth: rz2
        };
    }

    // 画地面网格
    ctx.strokeStyle = '#1a2040';
    ctx.lineWidth = 1;
    const gridSize = Math.max(maxX-minX, maxZ-minZ) + 4;
    const gx0 = (minX + maxX) / 2 - gridSize/2;
    const gz0 = (minZ + maxZ) / 2 - gridSize/2;
    for (let i = 0; i <= gridSize; i += 2) {
        const p1 = project(gx0 + i, minY - 0.5, gz0, 0);
        const p2 = project(gx0 + i, minY - 0.5, gz0 + gridSize, 0);
        ctx.beginPath(); ctx.moveTo(p1.sx, p1.sy); ctx.lineTo(p2.sx, p2.sy); ctx.stroke();
        const p3 = project(gx0, minY - 0.5, gz0 + i, 0);
        const p4 = project(gx0 + gridSize, minY - 0.5, gz0 + i, 0);
        ctx.beginPath(); ctx.moveTo(p3.sx, p3.sy); ctx.lineTo(p4.sx, p4.sy); ctx.stroke();
    }

    // 按深度排序方块
    const projected = previewBlocks.map(b => {
        const p = project(b.x, b.y, b.z);
        return { ...b, ...p };
    });
    projected.sort((a, b) => a.depth - b.depth);

    // 画方块
    const blockSize = Math.max(2, scale * 0.9);
    for (const b of projected) {
        const color = b.color || '#888888';
        ctx.fillStyle = color;
        ctx.fillRect(b.sx - blockSize/2, b.sy - blockSize/2, blockSize, blockSize);
        ctx.strokeStyle = 'rgba(255,255,255,0.15)';
        ctx.lineWidth = 1;
        ctx.strokeRect(b.sx - blockSize/2, b.sy - blockSize/2, blockSize, blockSize);
    }
}

// 拖拽旋转
document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('previewCanvas');
    canvas.addEventListener('mousedown', function(e) {
        previewState.dragging = true;
        previewState.lastX = e.clientX;
        previewState.lastY = e.clientY;
    });
    document.addEventListener('mousemove', function(e) {
        if (!previewState.dragging) return;
        const dx = e.clientX - previewState.lastX;
        const dy = e.clientY - previewState.lastY;
        previewState.angleY += dx * 0.01;
        previewState.angleX += dy * 0.01;
        previewState.angleX = Math.max(-1.5, Math.min(1.5, previewState.angleX));
        previewState.lastX = e.clientX;
        previewState.lastY = e.clientY;
        renderPreview();
    });
    document.addEventListener('mouseup', function() { previewState.dragging = false; });
    // 触摸支持
    canvas.addEventListener('touchstart', function(e) {
        e.preventDefault();
        const t = e.touches[0];
        previewState.dragging = true;
        previewState.lastX = t.clientX;
        previewState.lastY = t.clientY;
    });
    canvas.addEventListener('touchmove', function(e) {
        e.preventDefault();
        if (!previewState.dragging) return;
        const t = e.touches[0];
        const dx = t.clientX - previewState.lastX;
        const dy = t.clientY - previewState.lastY;
        previewState.angleY += dx * 0.01;
        previewState.angleX += dy * 0.01;
        previewState.angleX = Math.max(-1.5, Math.min(1.5, previewState.angleX));
        previewState.lastX = t.clientX;
        previewState.lastY = t.clientY;
        renderPreview();
    });
    canvas.addEventListener('touchend', function() { previewState.dragging = false; });
    // 初始空预览
    renderPreview();
});
// 初始化
fetch('/api?action=info').then(r=>r.json()).then(data => {
    document.getElementById('pathInfo').textContent = 'Mod 目录: ' + data.mods_dir;
    if(data.exists) setStatus('✅ Luanti 目录就绪', 'status-ok');
    else setStatus('⚠️ Luanti 目录不存在，可能需要手动设置', 'status-warn');
});
// 加载世界列表
fetch('/api?action=worlds').then(r=>r.json()).then(data => {
    const sel = document.getElementById('worldSelect');
    (data.worlds || []).forEach(w => {
        const opt = document.createElement('option');
        opt.value = w.dir;
        opt.textContent = w.name;
        sel.appendChild(opt);
    });
});
// 加载 AI 配置
loadAIConfig();
</script>
</body>
</html>'''

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        if parsed.path == '/':
            self._send_html(HTML_PAGE)
        elif parsed.path == '/api':
            action = qs.get('action', [''])[0]
            user_input = qs.get('input', [''])[0]

            if action == 'info':
                mods_dir = get_minetest_dir() / 'mods'
                self._send_json({"mods_dir": str(mods_dir), "exists": mods_dir.exists()})
            elif action == 'parse':
                params = parse_input(user_input)
                self._send_json({"params": params})
            elif action == 'generate':
                params = parse_input(user_input)
                lua = gen_lua(params)
                self._send_json({"lua": lua})
            elif action == 'install':
                params = parse_input(user_input)
                lua = gen_lua(params)
                path = install_mod(lua)
                self._send_json({"lua": lua, "path": path})
            elif action == 'preview':
                params = parse_input(user_input)
                blocks = gen_preview_blocks(params)
                self._send_json({"blocks": blocks})
            elif action == 'launch':
                result = launch_luanti()
                self._send_json(result)
            elif action == 'join':
                # 一键加入: 安装mod → 启用到世界 → 启动游戏进入世界
                params = parse_input(user_input)
                lua = gen_lua(params)
                mod_path = install_mod(lua)
                # 选择世界
                world_name = qs.get('world', [''])[0]
                mt_dir = get_minetest_dir()
                if world_name:
                    world_dir = str(mt_dir / "worlds" / world_name)
                else:
                    world_dir = None
                world_path = enable_mod_in_world(world_dir)
                launch_result = launch_luanti(world_path)
                self._send_json({
                    "lua": lua,
                    "mod_path": mod_path,
                    "world_path": world_path,
                    "launch": launch_result,
                    "message": "已安装mod并启动游戏，进入后输入 /build 生成建筑"
                })
            elif action == 'worlds':
                # 列出所有可用世界
                worlds = list_worlds()
                self._send_json({"worlds": worlds})
            elif action == 'setworld':
                # 设置默认世界
                world_name = qs.get('world', [''])[0]
                mt_dir = get_minetest_dir()
                world_dir = mt_dir / "worlds" / world_name
                if world_dir.exists():
                    self._send_json({"success": True, "world": world_name, "path": str(world_dir)})
                else:
                    self._send_json({"error": f"世界不存在: {world_name}"})
            elif action == 'ai_generate':
                # AI 大模型生成
                api_key = qs.get('api_key', [''])[0]
                base_url = qs.get('base_url', ['https://api.deepseek.com/v1'])[0]
                model = qs.get('model', ['deepseek-chat'])[0]
                if not api_key:
                    self._send_json({"error": "请先设置 API Key"})
                    return
                try:
                    content = call_llm(api_key, base_url, model, user_input)
                    cmds = parse_llm_json(content)
                    if not cmds:
                        self._send_json({"error": "AI 返回格式错误", "raw": content[:500]})
                        return
                    blocks = cmds_to_blocks(cmds) if isinstance(cmds, list) else cmds_to_blocks(cmds.get("cmds",[]))
                    if not blocks:
                        self._send_json({"error": "AI 生成的命令无法转为方块"})
                        return
                    lua, valid_blocks = blocks_to_lua(blocks, user_input)
                    self._send_json({"lua": lua, "blocks": valid_blocks, "count": len(valid_blocks)})
                except Exception as e:
                    self._send_json({"error": str(e)})
            elif action == 'ai_preview':
                # AI 预览 (只生成方块列表，不安装)
                api_key = qs.get('api_key', [''])[0]
                base_url = qs.get('base_url', ['https://api.deepseek.com/v1'])[0]
                model = qs.get('model', ['deepseek-chat'])[0]
                if not api_key:
                    self._send_json({"error": "请先设置 API Key"})
                    return
                try:
                    content = call_llm(api_key, base_url, model, user_input)
                    cmds = parse_llm_json(content)
                    if not cmds:
                        self._send_json({"error": "AI 返回格式错误", "raw": content[:500]})
                        return
                    blocks = cmds_to_blocks(cmds) if isinstance(cmds, list) else cmds_to_blocks(cmds.get("cmds",[]))
                    if not blocks:
                        self._send_json({"error": "AI 命令无法转为方块"})
                        return
                    preview_blocks = []
                    for b in blocks:
                        btype = b.get("type", "stone")
                        color = BLOCK_TYPE_TO_COLOR.get(btype, "#7f8c8d")
                        preview_blocks.append({"x": b["x"], "y": b["y"], "z": b["z"], "color": color})
                    self._send_json({"blocks": preview_blocks, "count": len(preview_blocks)})
                except Exception as e:
                    self._send_json({"error": str(e)})
            elif action == 'ai_install':
                # AI 生成 + 安装 + 可选启动
                api_key = qs.get('api_key', [''])[0]
                base_url = qs.get('base_url', ['https://api.deepseek.com/v1'])[0]
                model = qs.get('model', ['deepseek-chat'])[0]
                world_name = qs.get('world', [''])[0]
                if not api_key:
                    self._send_json({"error": "请先设置 API Key"})
                    return
                try:
                    content = call_llm(api_key, base_url, model, user_input)
                    cmds = parse_llm_json(content)
                    if not cmds:
                        self._send_json({"error": "AI 返回格式错误", "raw": content[:500]})
                        return
                    blocks = cmds_to_blocks(cmds) if isinstance(cmds, list) else cmds_to_blocks(cmds.get("cmds",[]))
                    if not blocks:
                        self._send_json({"error": "AI 命令无法转为方块"})
                        return
                    lua, valid_blocks = blocks_to_lua(blocks, user_input)
                    mod_path = install_mod(lua)
                    # 启用世界
                    mt_dir = get_minetest_dir()
                    if world_name:
                        world_dir = str(mt_dir / "worlds" / world_name)
                    else:
                        world_dir = None
                    world_path = enable_mod_in_world(world_dir)
                    launch_result = launch_luanti(world_path)
                    # 预览方块
                    preview_blocks = []
                    for b in valid_blocks:
                        color = BLOCK_TYPE_TO_COLOR.get(b.get("type", "stone"), "#7f8c8d")
                        preview_blocks.append({"x": b["x"], "y": b["y"], "z": b["z"], "color": color})
                    self._send_json({
                        "lua": lua,
                        "blocks": preview_blocks,
                        "count": len(valid_blocks),
                        "mod_path": mod_path,
                        "world_path": world_path,
                        "launch": launch_result,
                    })
                except Exception as e:
                    self._send_json({"error": str(e)})
            else:
                self._send_json({"error": "未知操作"})
        else:
            self._send_404()

    def _send_html(self, html):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def _send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _send_404(self):
        self.send_response(404)
        self.end_headers()

    def log_message(self, *args):
        pass  # 静默日志

def main():
    port = 8765
    server = HTTPServer(('127.0.0.1', port), Handler)
    url = f'http://localhost:{port}'
    print(f'🏗️  Luanti 自然语言建筑生成器')
    print(f'📍 浏览器打开: {url}')
    print(f'📁 Mod 目录: {get_minetest_dir() / "mods"}')
    print(f'按 Ctrl+C 停止')

    # 自动打开浏览器
    import subprocess
    system = platform.system()
    if system == 'Darwin':
        subprocess.Popen(['open', url])
    elif system == 'Linux':
        subprocess.Popen(['xdg-open', url])
    elif system == 'Windows':
        subprocess.Popen(['cmd', '/c', 'start', url])

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n已停止')
        server.shutdown()

if __name__ == '__main__':
    main()
