"""Luanti Builder - lua_gen 模块。"""

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
    color = params["color"]
    size = params["size"]
    material = params["material"]
    features = params["features"]
    if not color and not material:
        color = "gray"  # 无颜色无材质时才默认灰色
    sm = [0.6,1.0,1.5,2.5][size]
    block = select_block(color, material)
    builder = gen_builder(btype, block, sm, features)

    lua = f'''-- nl_builder mod - 自然语言生成
-- 输入: {params["raw"]}
-- 类型: {btype}, 颜色: {color or "-"}, 材质: {material or "-"}, 尺寸: {sm}x

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
    elif btype == "windmill":
        wh = int(12*s); wr = max(2, int(3*s)); bl = int(wr*2)
        return f"""local function build_structure(pos)
    local h = {wh} local w = {wr}
    fill_cylinder(pos, 0, 1, 0, w, h, B)
    for y=0, math.ceil(w/2) do
        local r = math.max(1, w - y)
        fill_cylinder(pos, 0, h+y+1, 0, r, 1, B)
    end
    local bh = h + math.ceil(w/2)
    for d=-{bl}, {bl} do
        minetest.set_node({{x=pos.x+d, y=pos.y+bh, z=pos.z}}, {{name=B}})
        minetest.set_node({{x=pos.x, y=pos.y+bh, z=pos.z+d}}, {{name=B}})
    end
    minetest.set_node({{x=pos.x, y=pos.y+h, z=pos.z}}, {{name='my_first_mod:brick_glow'}})
end"""
    elif btype == "pagoda":
        tiers = max(3, int(3*s + 1))
        tw0 = int(6*s); th = int(5*s)
        parts = []
        for t in range(tiers):
            tw = max(2, tw0 - t * (tw0 // tiers))
            ty = t * th + 1
            parts.append(f"fill_shell(pos, -{tw}, {ty}, -{tw}, {tw}, {ty+th}, {tw}, B)")
            parts.append(f'fill_box(pos, -{tw}-2, {ty+th}, -{tw}-2, {tw}+2, {ty+th}, {tw}+2, "default:wood")')
            parts.append(f"minetest.set_node({{x=pos.x, y=pos.y+{ty+th}+1, z=pos.z}}, {{name='my_first_mod:brick_glow'}})")
        tier_code = "\\n    ".join(parts)
        return f"""local function build_structure(pos)
    {tier_code}
end"""
    elif btype == "gazebo":
        gh = int(5*s); gw = int(4*s)
        return f"""local function build_structure(pos)
    local h = {gh} local w = {gw}
    for i=0, 7 do
        local angle = i * math.pi / 4
        local px = math.floor(math.cos(angle) * w)
        local pz = math.floor(math.sin(angle) * w)
        for y=1, h do
            minetest.set_node({{x=pos.x+px, y=pos.y+y, z=pos.z+pz}}, {{name=B}})
        end
    end
    for y=0, math.ceil(h/2) do
        local r = math.max(1, w - y)
        fill_cylinder(pos, 0, h+y+1, 0, r, 1, "default:wood")
    end
    minetest.set_node({{x=pos.x, y=pos.y+h, z=pos.z}}, {{name='my_first_mod:brick_glow'}})
end"""
    elif btype == "skyscraper":
        sh = int(30*s); sw = max(3, int(5*s))
        return f"""local function build_structure(pos)
    local h = {sh} local w = {sw}
    fill_shell(pos, -w, 1, -w, w, h, w, B)
    for y=2, h, 2 do
        for x=-w, w, 2 do
            minetest.set_node({{x=pos.x+x, y=pos.y+y, z=pos.z-w}}, {{name='default:glass'}})
            minetest.set_node({{x=pos.x+x, y=pos.y+y, z=pos.z+w}}, {{name='default:glass'}})
        end
        for z=-w, w, 2 do
            minetest.set_node({{x=pos.x-w, y=pos.y+y, z=pos.z+z}}, {{name='default:glass'}})
            minetest.set_node({{x=pos.x+w, y=pos.y+y, z=pos.z+z}}, {{name='default:glass'}})
        end
    end
    for y=h+1, h+math.ceil(w/2) do
        minetest.set_node({{x=pos.x, y=pos.y+y, z=pos.z}}, {{name=B}})
    end
    minetest.set_node({{x=pos.x, y=pos.y+h+math.ceil(w/2)+1, z=pos.z}}, {{name='my_first_mod:brick_glow'}})
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
