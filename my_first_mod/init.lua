-- my_first_mod/init.lua
-- 示例 Mod：自定义方块、工具、合成配方、聊天命令 + 饥饿系统 + 自定义生物

-- ============================================================
-- 配置常量
-- ============================================================
local HUNGER_MAX = 20
local HUNGER_TICK = 30.0       -- 每30秒消耗1点饱食度（原4秒太快）
local HUNGER_STARVE_DMG = 1
local HUNGER_HEAL_THRESHOLD = 18
local HUNGER_HEAL_AMOUNT = 1
local HUNGER_HEAL_INTERVAL = 6.0
local SPRINT_COST = 0.15      -- 疾跑消耗降低
local SPRINT_SPEED = 1.8

-- 生物刷新配置
local SPAWN_INTERVAL = 90       -- 刷新检查间隔（秒）
local SPAWN_CHANCE = 500        -- 每次检查刷新概率 (1/chance)
local MAX_MOBS_NEAR_PLAYER = 3  -- 玩家附近最大生物数
local SPAWN_RADIUS = 16         -- 刷新范围

-- ============================================================
-- 1. 注册自定义方块 (Node)
-- ============================================================

minetest.register_node("my_first_mod:glow_block", {
    description = "发光方块",
    tiles = {"my_first_mod_glow_block.png"},
    light_source = minetest.LIGHT_MAX,
    groups = {cracky = 3, oddly_breakable_by_hand = 2},
    is_ground_content = false,
})

minetest.register_node("my_first_mod:super_block", {
    description = "超硬方块",
    tiles = {"my_first_mod_super_block.png"},
    groups = {cracky = 1, level = 3},
    is_ground_content = false,
    sounds = default.node_sound_stone_defaults(),
})

-- ============================================================
-- 2. 注册自定义工具 (Tool)
-- ============================================================

minetest.register_tool("my_first_mod:super_pickaxe", {
    description = "超级镐子",
    inventory_image = "my_first_mod_super_pickaxe.png",
    tool_capabilities = {
        full_punch_interval = 0.5,
        max_drop_level = 5,
        groupcaps = {
            cracky = {
                times = {[1] = 0.5, [2] = 0.2, [3] = 0.1},
                uses = 500,
                maxlevel = 5,
            },
            crumbly = {
                times = {[1] = 0.5, [2] = 0.2, [3] = 0.1},
                uses = 500,
                maxlevel = 5,
            },
        },
        damage_groups = {fleshy = 10},
    },
})

-- ============================================================
-- 3. 注册合成配方 (Crafting Recipe)
-- ============================================================

minetest.register_craft({
    output = "my_first_mod:super_block",
    recipe = {
        {"my_first_mod:glow_block", "my_first_mod:glow_block", "my_first_mod:glow_block"},
        {"my_first_mod:glow_block", "my_first_mod:glow_block", "my_first_mod:glow_block"},
        {"my_first_mod:glow_block", "my_first_mod:glow_block", "my_first_mod:glow_block"},
    },
})

minetest.register_craft({
    output = "my_first_mod:super_pickaxe",
    recipe = {
        {"my_first_mod:super_block", "my_first_mod:super_block", "my_first_mod:super_block"},
        {"", "group:stick", ""},
        {"", "group:stick", ""},
    },
})

-- ============================================================
-- 4. 饥饿系统
-- ============================================================

local hunger_state = {}

local function get_hunger(player)
    local name = player:get_player_name()
    if not hunger_state[name] then
        hunger_state[name] = {
            hunger = HUNGER_MAX,
            timer = 0,
            heal_timer = 0,
            sprint_timer = 0,
            sprinting = false,
        }
    end
    return hunger_state[name]
end

local function update_hud(player, hunger)
    local name = player:get_player_name()
    local state = hunger_state[name]
    if state and state.hud_fg_id then
        player:hud_change(state.hud_fg_id, "number", math.floor(hunger))
    end
end

minetest.register_on_joinplayer(function(player)
    local state = get_hunger(player)
    state.hunger = HUNGER_MAX
    state.timer = 0
    state.heal_timer = 0

    state.hud_bg_id = player:hud_add({
        type = "statbar",
        position = {x = 0.5, y = 1.0},
        offset = {x = 15, y = -87},
        size = {x = 24, y = 24},
        text = "my_first_mod_hunger_bg.png",
        number = HUNGER_MAX,
        alignment = {x = -1, y = -1},
    })

    state.hud_fg_id = player:hud_add({
        type = "statbar",
        position = {x = 0.5, y = 1.0},
        offset = {x = 15, y = -87},
        size = {x = 24, y = 24},
        text = "my_first_mod_hunger_fg.png",
        number = HUNGER_MAX,
        alignment = {x = -1, y = -1},
    })

    -- FPS HUD (左上角)
    state._fps_hud_id = player:hud_add({
        type = "text",
        position = {x = 0, y = 0},
        offset = {x = 10, y = 10},
        text = "FPS: --",
        alignment = {x = 1, y = 1},
        scale = {x = 100, y = 100},
        number = 0xFFFFFF,
    })

    update_hud(player, HUNGER_MAX)
end)

minetest.register_on_leaveplayer(function(player)
    local name = player:get_player_name()
    hunger_state[name] = nil
end)

local global_timer = 0
local sprint_timer = 0
minetest.register_globalstep(function(dtime)
    -- ===== FPS HUD + 无敌回血 =====
    local players = minetest.get_connected_players()
    for _, player in ipairs(players) do
        local name = player:get_player_name()
        -- 无敌：持续满血
        if player:get_hp() < 20 then
            player:set_hp(20)
        end
        local state = hunger_state[name]
        if not state then goto fps_continue end

        -- FPS 计数
        state._fps_count = (state._fps_count or 0) + 1
        state._fps_timer = (state._fps_timer or 0) + dtime
        if state._fps_timer >= 1 then
            local fps = math.floor(state._fps_count / state._fps_timer)
            state._fps_count = 0
            state._fps_timer = 0
            if state._fps_hud_id then
                player:hud_change(state._fps_hud_id, "text", string.format("FPS: %d", fps))
            end
        end

        ::fps_continue::
    end

    -- ===== 疾跑检测（每帧但极轻量）=====
    sprint_timer = sprint_timer + dtime
    if sprint_timer >= 0.2 then
        sprint_timer = 0
        for _, player in ipairs(players) do
            local name = player:get_player_name()
            local state = hunger_state[name]
            if not state then goto sprint_continue end
            local keys = player:get_player_control()
            local moving = keys.up or keys.down or keys.left or keys.right
            if keys.aux1 and moving and state.hunger > 0 and not state.sprinting then
                state.sprinting = true
                player:set_physics_override({speed = SPRINT_SPEED})
            elseif (not keys.aux1 or not moving or state.hunger <= 0) and state.sprinting then
                state.sprinting = false
                player:set_physics_override({speed = 1.0})
            end
            ::sprint_continue::
        end
    end

    -- ===== 饥饿/治疗/光照（每2秒）=====
    global_timer = global_timer + dtime
    if global_timer < 2 then return end
    local elapsed = global_timer
    global_timer = 0

    for _, player in ipairs(players) do
        local name = player:get_player_name()
        local state = hunger_state[name]
        if not state then goto continue end

        state.timer = state.timer + elapsed
        state.heal_timer = state.heal_timer + elapsed
        state.sprint_timer = state.sprint_timer + elapsed

        if state.timer >= HUNGER_TICK then
            state.timer = state.timer - HUNGER_TICK
            state.hunger = math.max(0, state.hunger - 1)
            update_hud(player, state.hunger)
        end

        if state.sprinting and state.sprint_timer >= 1 then
            state.sprint_timer = state.sprint_timer - 1
            state.hunger = math.max(0, state.hunger - SPRINT_COST)
            update_hud(player, state.hunger)
            if state.hunger <= 0 then
                state.sprinting = false
                player:set_physics_override({speed = 1.0})
            end
        end

        -- 饥饿不再扣血，仅影响疾跑

        if state.hunger >= HUNGER_HEAL_THRESHOLD and state.heal_timer >= HUNGER_HEAL_INTERVAL then
            state.heal_timer = 0
            local hp = player:get_hp()
            if hp < 20 then
                player:set_hp(hp + HUNGER_HEAL_AMOUNT)
            end
        end

        -- 光照（合并到这里，每2秒更新）
        local tod = minetest.get_timeofday()
        if tod > 0.25 and tod < 0.75 then
            player:override_day_night_ratio(0.95)
        elseif tod >= 0.75 and tod < 0.85 then
            local t = (tod - 0.75) / 0.1
            player:override_day_night_ratio(0.95 - t * 0.7)
        elseif tod >= 0.85 or tod < 0.15 then
            player:override_day_night_ratio(0.25)
        else
            local t = (tod - 0.15) / 0.1
            player:override_day_night_ratio(0.25 + t * 0.7)
        end

        ::continue::
    end
end)

local function make_food(item_name, restore, desc)
    minetest.register_craftitem(item_name, {
        description = desc,
        inventory_image = item_name:gsub(":", "_") .. ".png",
        on_use = function(itemstack, user, pointed_thing)
            if not user or not user:is_player() then return itemstack end
            local state = get_hunger(user)
            if state.hunger >= HUNGER_MAX then
                minetest.chat_send_player(user:get_player_name(), "你已经吃饱了！")
                return itemstack
            end
            state.hunger = math.min(HUNGER_MAX, state.hunger + restore)
            update_hud(user, state.hunger)
            itemstack:take_item(1)
            return itemstack
        end,
    })
end

make_food("my_first_mod:bread", 10, "面包")
make_food("my_first_mod:apple", 6, "苹果")
make_food("my_first_mod:cooked_meat", 14, "烤肉")

minetest.register_craft({
    output = "my_first_mod:bread 2",
    recipe = {{"farming:wheat", "farming:wheat", "farming:wheat"}},
})

minetest.register_craft({
    type = "cooking",
    output = "my_first_mod:cooked_meat",
    recipe = "my_first_mod:raw_meat",
})

-- ============================================================
-- 5. 疾跑系统
-- ============================================================

-- (疾跑检测已合并到上面的主 globalstep 中)

-- ============================================================
-- 6. 自定义生物系统
-- ============================================================

-- 通用 AI 辅助函数
local function find_nearby_player(self, radius)
    local pos = self.object:get_pos()
    for _, obj in ipairs(minetest.get_objects_inside_radius(pos, radius or 16)) do
        if obj:is_player() then
            return obj, obj:get_pos()
        end
    end
    return nil, nil
end

local function find_nearest_player(pos, radius)
    local nearest = nil
    local nearest_dist = radius or 999
    for _, obj in ipairs(minetest.get_objects_inside_radius(pos, radius or 32)) do
        if obj:is_player() then
            local p = obj:get_pos()
            local dist = vector.distance(pos, p)
            if dist < nearest_dist then
                nearest = obj
                nearest_dist = dist
            end
        end
    end
    return nearest, nearest_dist
end

local function random_walk(self, speed)
    if not self._walk_timer then self._walk_timer = 0 end
    self._walk_timer = self._walk_timer - 1

    if self._walk_timer <= 0 then
        self._walk_timer = math.random(60, 180)
        local yaw = math.random() * math.pi * 2
        self.object:set_yaw(yaw)
        local vel = {
            x = math.cos(yaw) * speed,
            y = self.object:get_velocity().y,
            z = math.sin(yaw) * speed,
        }
        self.object:set_velocity(vel)
        self:set_animation("walk")
    end
end

local function stop_walking(self)
    local vel = self.object:get_velocity()
    self.object:set_velocity({x = 0, y = vel.y, z = 0})
    self:set_animation("stand")
end

-- ---------- 友好动物：小猪 ----------

minetest.register_entity("my_first_mod:pig", {
    initial_properties = {
        visual = "upright_sprite",
        textures = {"my_first_mod_pig_front.png", "my_first_mod_pig_side.png"},
        visual_size = {x = 1.5, y = 1.5},
        collisionbox = {-0.4, 0, -0.4, 0.4, 1.2, 0.4},
        physical = true,
        hp_max = 15,
        stepheight = 1.1,
    },

    _timer = 0,
    _walk_timer = 0,
    _panic_timer = 0,
    _breed_cooldown = 0,

    on_activate = function(self, staticdata)
        self._timer = 0
        self._walk_timer = 0
        self._panic_timer = 0
        self._breed_cooldown = 0
        if self.set_animation then self:set_animation("stand") end
    end,

    set_animation = function(self, anim)
        -- upright_sprite / cube 无骨骼动画，用发光模拟状态
        if anim == "attack" then
            self.object:set_texture_mod("^[brighten")
        else
            self.object:set_texture_mod("")
        end
    end,

    on_punch = function(self, puncher, time_from_last_punch, tool_capabilities, dir)
        local dmg = 0
        if tool_capabilities and tool_capabilities.damage_groups then
            dmg = tool_capabilities.damage_groups.fleshy or 1
        end
        local hp = self.object:get_hp()
        self.object:set_hp(hp - dmg)

        -- 受惊逃跑
        self._panic_timer = 60
        if dir then
            local yaw = math.atan2(dir.z, dir.x) + math.pi
            self.object:set_yaw(yaw)
            local v = self.object:get_velocity()
            self.object:set_velocity({x = math.cos(yaw) * 4, y = v.y, z = math.sin(yaw) * 4})
        end

        if self.object:get_hp() <= 0 then
            -- 掉落物品
            local pos = self.object:get_pos()
            minetest.add_item(pos, "my_first_mod:raw_meat " .. math.random(1, 3))
            self.object:remove()
        end
    end,

    on_rightclick = function(self, clicker)
        if not clicker or not clicker:is_player() then return end
        local item = clicker:get_wielded_item()
        local itemname = item:get_name()

        -- 用苹果喂食繁殖
        if itemname == "my_first_mod:apple" and self._breed_cooldown <= 0 then
            item:take_item(1)
            clicker:set_wielded_item(item)
            self._breed_cooldown = 300

            -- 生成一只小猪
            local pos = self.object:get_pos()
            local child = minetest.add_entity(pos, "my_first_mod:pig")
            if child then
                local ent = child:get_luaentity()
                child:set_properties({visual_size = {x = 0.5, y = 0.5}})
                ent._breed_cooldown = 600
            end
            minetest.chat_send_player(clicker:get_player_name(), "小猪出生了！")
        end
    end,

    on_step = function(self, dtime)
        self._timer = self._timer + dtime
        if self._timer < 1.5 then return end
        self._timer = 0

        if self._breed_cooldown > 0 then
            self._breed_cooldown = self._breed_cooldown - 1
        end

        -- 受惊逃跑
        if self._panic_timer > 0 then
            self._panic_timer = self._panic_timer - 1
            if self._panic_timer <= 0 then
                stop_walking(self)
            end
            return
        end

        -- 随机游走
        random_walk(self, 2)
    end,
})

-- ---------- 敌对怪物：暗影怪 ----------

minetest.register_entity("my_first_mod:shadow", {
    initial_properties = {
        visual = "cube",
        textures = {
            "my_first_mod_shadow_top.png", "my_first_mod_shadow_top.png",
            "my_first_mod_shadow_side.png", "my_first_mod_shadow_side.png",
            "my_first_mod_shadow_front.png", "my_first_mod_shadow_front.png",
        },
        visual_size = {x = 1, y = 1.5, z = 1},
        collisionbox = {-0.4, -0.01, -0.4, 0.4, 1.8, 0.4},
        physical = true,
        hp_max = 25,
        stepheight = 1.1,
        glow = 4,
    },

    _timer = 0,
    _state = "wander",  -- wander | chase | attack
    _target = nil,
    _attack_timer = 0,

    on_activate = function(self, staticdata)
        self._timer = 0
        self._state = "wander"
        self._target = nil
        self._attack_timer = 0
    end,

    set_animation = function(self, anim)
        if anim == "attack" then
            self.object:set_texture_mod("^[brighten^[invert:b")
        else
            self.object:set_texture_mod("")
        end
    end,

    on_punch = function(self, puncher, time_from_last_punch, tool_capabilities, dir)
        local dmg = 0
        if tool_capabilities and tool_capabilities.damage_groups then
            dmg = tool_capabilities.damage_groups.fleshy or 1
        end
        local hp = self.object:get_hp()
        self.object:set_hp(hp - dmg)

        -- 被攻击后追击攻击者
        if puncher and puncher:is_player() then
            self._target = puncher
            self._state = "chase"
        end

        if self.object:get_hp() <= 0 then
            local pos = self.object:get_pos()
            minetest.add_item(pos, "my_first_mod:glow_block " .. math.random(1, 2))
            -- 粒子效果
            minetest.add_particlespawner({
                amount = 20,
                time = 0.5,
                minpos = pos,
                maxpos = vector.add(pos, {x = 1, y = 2, z = 1}),
                minvel = {x = -2, y = 2, z = -2},
                maxvel = {x = 2, y = 4, z = 2},
                minacc = {x = 0, y = -5, z = 0},
                maxacc = {x = 0, y = -5, z = 0},
                minsize = 1,
                maxsize = 3,
                texture = "my_first_mod_super_block.png",
                glow = 10,
            })
            self.object:remove()
        end
    end,

    on_step = function(self, dtime)
        self._timer = self._timer + dtime
        if self._timer < 1.0 then return end
        self._timer = 0
        self._attack_timer = self._attack_timer - 1

        local pos = self.object:get_pos()

        -- 检测最近玩家
        local player, dist = find_nearest_player(pos, 16)

        if player then
            if dist < 2 then
                -- 攻击范围
                self._state = "attack"
                self._target = player
            elseif dist < 12 then
                -- 追击
                self._state = "chase"
                self._target = player
            end
        elseif self._state == "chase" and (not player or dist > 20) then
            self._state = "wander"
            self._target = nil
        end

        if self._state == "attack" and self._target then
            -- 攻击玩家
            if self._attack_timer <= 0 then
                self._attack_timer = 30  -- 1.5秒冷却（每0.3秒tick）
                local ppos = self._target:get_pos()
                local dir = vector.direction(pos, ppos)
                -- 瞄准玩家
                self.object:set_yaw(math.atan2(dir.z, dir.x))
                self:set_animation("attack")
                if vector.distance(pos, ppos) < 2.5 then
                    self._target:set_hp(self._target:get_hp() - 3)
                end
            end

        elseif self._state == "chase" and self._target then
            -- 朝玩家移动
            local ppos = self._target:get_pos()
            local dir = vector.direction(pos, ppos)
            self.object:set_yaw(math.atan2(dir.z, dir.x))
            local vel = self.object:get_velocity()
            self.object:set_velocity({
                x = dir.x * 3.5,
                y = vel.y,
                z = dir.z * 3.5,
            })
            self:set_animation("walk")

        else
            -- 随机游走
            random_walk(self, 1.5)
        end
    end,
})

-- ---------- 生物刷新机制 ----------

local spawn_timer = 0
minetest.register_globalstep(function(dtime)
    spawn_timer = spawn_timer + dtime
    if spawn_timer < SPAWN_INTERVAL then return end
    spawn_timer = 0

    for _, player in ipairs(minetest.get_connected_players()) do
        local ppos = player:get_pos()

        -- 检查附近已有生物数量
        local nearby_mobs = 0
        for _, obj in ipairs(minetest.get_objects_inside_radius(ppos, SPAWN_RADIUS)) do
            local ent = obj:get_luaentity()
            if ent and (ent.name == "my_first_mod:pig" or ent.name == "my_first_mod:shadow") then
                nearby_mobs = nearby_mobs + 1
            end
        end

        if nearby_mobs >= MAX_MOBS_NEAR_PLAYER then
            goto continue
        end

        if math.random(1, SPAWN_CHANCE) > 1 then
            goto continue
        end

        -- 随机选一个位置
        local angle = math.random() * math.pi * 2
        local dist = math.random(8, SPAWN_RADIUS)
        local spawn_pos = {
            x = ppos.x + math.cos(angle) * dist,
            y = ppos.y,
            z = ppos.z + math.sin(angle) * dist,
        }

        -- 找地面高度
        local node = minetest.get_node_or_nil(spawn_pos)
        if not node then goto continue end

        -- 向上找空气
        for i = 1, 5 do
            local above = minetest.get_node_or_nil({x = spawn_pos.x, y = spawn_pos.y + i, z = spawn_pos.z})
            local below = minetest.get_node_or_nil({x = spawn_pos.x, y = spawn_pos.y + i - 1, z = spawn_pos.z})
            if above and below then
                local above_def = minetest.registered_nodes[above.name]
                local below_def = minetest.registered_nodes[below.name]
                if above_def and above_def.walkable == false and below_def and below_def.walkable == true then
                    spawn_pos.y = spawn_pos.y + i
                    break
                end
            end
        end

        -- 随机生成猪或暗影怪
        local mob_type = math.random(1, 3)
        if mob_type <= 2 then
            minetest.add_entity(spawn_pos, "my_first_mod:pig")
        else
            minetest.add_entity(spawn_pos, "my_first_mod:shadow")
        end

        ::continue::
    end
end)

-- ---------- 掉落物注册 ----------

minetest.register_craftitem("my_first_mod:raw_meat", {
    description = "生肉",
    inventory_image = "my_first_mod_raw_meat.png",
    on_use = function(itemstack, user, pointed_thing)
        if not user or not user:is_player() then return itemstack end
        local state = get_hunger(user)
        state.hunger = math.min(HUNGER_MAX, state.hunger + 3)
        update_hud(user, state.hunger)
        itemstack:take_item(1)
        return itemstack
    end,
})

-- ---------- 召唤生物命令 ----------

minetest.register_chatcommand("summon", {
    description = "召唤生物 (pig / shadow)",
    params = "<mob_name>",
    func = function(name, param)
        local player = minetest.get_player_by_name(name)
        if not player then return false, "玩家不存在" end
        local mob_name = (param or ""):trim()
        if mob_name ~= "pig" and mob_name ~= "shadow" then
            return false, "用法: /summon pig 或 /summon shadow"
        end
        local pos = player:get_pos()
        pos.y = pos.y + 1
        minetest.add_entity(pos, "my_first_mod:" .. mob_name)
        return true, "已召唤 " .. mob_name .. "！"
    end,
})

-- ============================================================
-- 7. 聊天命令
-- ============================================================

minetest.register_chatcommand("giveglow", {
    description = "给你发光方块 x64",
    func = function(name, param)
        local player = minetest.get_player_by_name(name)
        if not player then return false, "玩家不存在" end
        player:get_inventory():add_item("main", "my_first_mod:glow_block 64")
        return true, "获得 64 个发光方块！"
    end,
})

minetest.register_chatcommand("heal", {
    description = "恢复满血满饱食度",
    func = function(name, param)
        local player = minetest.get_player_by_name(name)
        if not player then return false, "玩家不存在" end
        player:set_hp(20)
        local state = get_hunger(player)
        state.hunger = HUNGER_MAX
        update_hud(player, state.hunger)
        return true, "已恢复满血满饱食度！"
    end,
})

-- /fly 切换飞行模式 (可以飞出水面)
minetest.register_chatcommand("fly", {
    description = "切换飞行模式",
    func = function(name, param)
        local player = minetest.get_player_by_name(name)
        if not player then return false, "玩家不存在" end
        local privs = minetest.get_player_privs(name)
        if privs.fly then
            privs.fly = nil
            minetest.set_player_privs(name, privs)
            return true, "飞行模式已关闭"
        else
            privs.fly = true
            minetest.set_player_privs(name, privs)
            return true, "飞行模式已开启！按空格起飞，再按空格悬停"
        end
    end,
})

-- /tp 传送到岸上 (传送到玩家上方最近的实地方块)
minetest.register_chatcommand("tptop", {
    description = "传送到上方地面",
    func = function(name, param)
        local player = minetest.get_player_by_name(name)
        if not player then return false, "玩家不存在" end
        local pos = player:get_pos()
        -- 向上找第一个实地方块
        for dy = 1, 100 do
            local node = minetest.get_node_or_nil({x=pos.x, y=pos.y+dy, z=pos.z})
            local above = minetest.get_node_or_nil({x=pos.x, y=pos.y+dy+1, z=pos.z})
            local def = node and minetest.registered_nodes[node.name]
            local adef = above and minetest.registered_nodes[above.name]
            if def and def.walkable and adef and not adef.walkable then
                player:set_pos({x=pos.x, y=pos.y+dy+1.5, z=pos.z})
                return true, "已传送到岸上！"
            end
        end
        return false, "上方100格内没有找到地面"
    end,
})

minetest.register_chatcommand("hunger", {
    description = "查看当前饱食度",
    func = function(name, param)
        local player = minetest.get_player_by_name(name)
        if not player then return false, "玩家不存在" end
        local state = get_hunger(player)
        return true, string.format("饱食度: %d / %d", math.floor(state.hunger), HUNGER_MAX)
    end,
})

-- ============================================================
-- 8. ABM
-- ============================================================

minetest.register_abm({
    nodenames = {"group:stone"},
    neighbors = {"my_first_mod:glow_block"},
    interval = 10,
    chance = 30,
    action = function(pos, node)
        minetest.set_node(pos, {name = "my_first_mod:glow_block"})
    end,
})

-- ============================================================
-- 9. 乐高风格天空与环境
-- ============================================================

minetest.register_on_joinplayer(function(player)
    -- 无敌模式：飞行 + 无伤 + 能跳上台阶
    player:set_physics_override({jump = 3.0, speed = 1.5, gravity = 1.0, sneak = false})
    local name = player:get_player_name()
    local privs = minetest.get_player_privs(name)
    privs.fly = true
    privs.fast = true
    privs.noclip = true
    minetest.set_player_privs(name, privs)

    -- 设置乐高风格天空：明亮蓝色天空、白色云
    player:set_sky({
        type = "regular",
        sky_color = {
            day_sky = "#5BAFE8",
            day_horizon = "#8FCCF0",
            dawn_sky = "#FF9966",
            dawn_horizon = "#FFCC88",
            night_sky = "#1A1A3E",
            night_horizon = "#333366",
            indoors = "#646464",
        },
        clouds = true,
    })

    -- 设置乐高风格的太阳
    player:set_sun({
        visible = true,
        texture = "default_cloud.png",
        tonemap = "default_cloud.png",
        scale = 3,
    })

    -- 设置乐高风格的月亮
    player:set_moon({
        visible = true,
        texture = "default_snow.png",
        tonemap = "default_snow.png",
        scale = 2,
    })

    -- 设置乐高风格的星星
    player:set_stars({
        visible = true,
        count = 100,
        star_color = "#FFFDD0",
        scale = 2,
    })

    -- 设置云
    player:set_clouds({
        density = 0.4,
        color = "#FFFFFFF0",
        ambient = "#000000",
        height = 120,
        thickness = 16,
        speed = {x = 2, y = 0},
    })

end)

-- (光照已合并到主 globalstep 中)

-- ============================================================
-- 10. 乐高积木搭建模式
-- ============================================================

-- 积木颜色系列 (鲜艳的乐高原色)
local BRICK_COLORS = {
    {name = "red",    r = 220, g = 50,  b = 50},
    {name = "blue",   r = 50,  g = 100, b = 220},
    {name = "yellow", r = 240, g = 210, b = 50},
    {name = "green",  r = 50,  g = 180, b = 70},
    {name = "white",  r = 245, g = 245, b = 250},
    {name = "black",  r = 40,  g = 40,  b = 45},
    {name = "orange", r = 240, g = 140, b = 30},
    {name = "purple", r = 150, g = 50,  b = 180},
    {name = "lime",   r = 130, g = 230, b = 50},
    {name = "cyan",   r = 50,  g = 200, b = 230},
    {name = "pink",   r = 240, g = 130, b = 170},
    {name = "gray",   r = 130, g = 130, b = 135},
}

-- 注册乐高积木方块
for _, c in ipairs(BRICK_COLORS) do
    minetest.register_node("my_first_mod:brick_" .. c.name, {
        description = "乐高积木 - " .. c.name,
        tiles = {
            "my_first_mod_brick_" .. c.name .. "_top.png",
            "my_first_mod_brick_" .. c.name .. "_bottom.png",
            "my_first_mod_brick_" .. c.name .. "_side.png",
            "my_first_mod_brick_" .. c.name .. "_side.png",
            "my_first_mod_brick_" .. c.name .. "_side.png",
            "my_first_mod_brick_" .. c.name .. "_side.png",
        },
        groups = {cracky = 2, oddly_breakable_by_hand = 1, lego_brick = 1},
        is_ground_content = false,
        sounds = default.node_sound_stone_defaults(),
        paramtype2 = "facedir",
    })
end

-- 发光积木（可做灯具）
minetest.register_node("my_first_mod:brick_glow", {
    description = "乐高发光积木",
    tiles = {"my_first_mod_brick_glow_top.png"},
    light_source = minetest.LIGHT_MAX,
    groups = {cracky = 2, oddly_breakable_by_hand = 1, lego_brick = 1},
    is_ground_content = false,
    sounds = default.node_sound_stone_defaults(),
})

-- 透明积木（可做窗户）
minetest.register_node("my_first_mod:brick_clear", {
    description = "乐高透明积木",
    tiles = {"my_first_mod_brick_clear_top.png"},
    use_texture_alpha = "blend",
    paramtype = "light",
    groups = {cracky = 2, oddly_breakable_by_hand = 1, lego_brick = 1},
    is_ground_content = false,
    sounds = default.node_sound_glass_defaults(),
})

-- 积木板（满格高度，玩家可跳上去）
minetest.register_node("my_first_mod:brick_plate", {
    description = "乐高积木板",
    tiles = {"my_first_mod_brick_plate_top.png"},
    groups = {cracky = 2, oddly_breakable_by_hand = 1, lego_brick = 1},
    is_ground_content = false,
    sounds = default.node_sound_stone_defaults(),
})

-- 搭建工具：积木清除器
minetest.register_tool("my_first_mod:brick_wand", {
    description = "积木魔杖（右键清除单个积木，潜行+右键清除区域3x3x3）",
    inventory_image = "my_first_mod_brick_wand.png",
    on_use = function(itemstack, user, pointed_thing)
        if not user or not user:is_player() then return end
        if pointed_thing.type ~= "node" then return end
        local pos = pointed_thing.under
        local node = minetest.get_node(pos)
        local def = minetest.registered_nodes[node.name]
        if def and def.groups and def.groups.lego_brick then
            minetest.remove_node(pos)
            minetest.add_item(pos, node.name)
        end
    end,
    on_place = function(itemstack, placer, pointed_thing)
        if not placer or not placer:is_player() then return itemstack end
        if pointed_thing.type ~= "node" then return itemstack end
        local pos = pointed_thing.under
        -- 潜行时清除 3x3x3
        if placer:get_player_control().sneak then
            for x = -1, 1 do
                for y = -1, 1 do
                    for z = -1, 1 do
                        local p = vector.add(pos, {x = x, y = y, z = z})
                        local node = minetest.get_node(p)
                        local def = minetest.registered_nodes[node.name]
                        if def and def.groups and def.groups.lego_brick then
                            minetest.remove_node(p)
                            minetest.add_item(p, node.name)
                        end
                    end
                end
            end
            minetest.chat_send_player(placer:get_player_name(), "已清除 3x3x3 积木区域")
        else
            local node = minetest.get_node(pos)
            local def = minetest.registered_nodes[node.name]
            if def and def.groups and def.groups.lego_brick then
                minetest.remove_node(pos)
                minetest.add_item(pos, node.name)
            end
        end
        return itemstack
    end,
})

-- 积木套装合成
for _, c in ipairs(BRICK_COLORS) do
    minetest.register_craft({
        output = "my_first_mod:brick_" .. c.name .. " 4",
        recipe = {
            {"default:clay_lump", "default:clay_lump", "default:clay_lump"},
            {"dye:" .. c.name, "dye:" .. c.name, "dye:" .. c.name},
        },
        replacements = {{"dye:" .. c.name, ""}},
    })
end

minetest.register_craft({
    output = "my_first_mod:brick_glow 4",
    recipe = {{"default:torch", "default:clay_lump", "default:torch"}},
})

minetest.register_craft({
    output = "my_first_mod:brick_clear 4",
    recipe = {{"default:glass", "default:clay_lump", "default:glass"}},
})

minetest.register_craft({
    output = "my_first_mod:brick_plate 4",
    recipe = {{"default:stone", "default:clay_lump", "default:stone"}},
})

minetest.register_craft({
    output = "my_first_mod:brick_wand",
    recipe = {
        {"", "default:diamond", ""},
        {"", "group:stick", ""},
        {"", "group:stick", ""},
    },
})

-- 给予积木套装命令
minetest.register_chatcommand("legokit", {
    description = "获得乐高积木套装（12色+发光+透明+板+魔杖）",
    func = function(name, param)
        local player = minetest.get_player_by_name(name)
        if not player then return false, "玩家不存在" end
        local inv = player:get_inventory()
        for _, c in ipairs(BRICK_COLORS) do
            inv:add_item("main", "my_first_mod:brick_" .. c.name .. " 32")
        end
        inv:add_item("main", "my_first_mod:brick_glow 16")
        inv:add_item("main", "my_first_mod:brick_clear 16")
        inv:add_item("main", "my_first_mod:brick_plate 16")
        inv:add_item("main", "my_first_mod:brick_wand")
        return true, "乐高积木套装已发放！"
    end,
})

-- ============================================================
-- 11. 清除残留村民实体（之前生成过的 villager 仍在存档中，激活时自动删除）
minetest.register_entity("my_first_mod:villager", {
    initial_properties = {
        visual = "upright_sprite",
        textures = {"blank.png"},
        visual_size = {x = 0, y = 0},
        collisionbox = {0, 0, 0, 0, 0, 0},
        physical = false,
        hp_max = 1,
        static_save = false,
    },
    on_activate = function(self, staticdata)
        self.object:remove()
    end,
})

-- 清除残留 text_sign 实体
minetest.register_entity("my_first_mod:text_sign", {
    initial_properties = {
        visual = "upright_sprite",
        textures = {"blank.png"},
        visual_size = {x = 0, y = 0},
        collisionbox = {0, 0, 0, 0, 0, 0},
        physical = false,
        hp_max = 1,
        static_save = false,
    },
    on_activate = function(self, staticdata)
        self.object:remove()
    end,
})

-- 建筑生成函数
local function build_house(pos, brick_color)
    local bname = "my_first_mod:brick_" .. brick_color
    local roof_color = brick_color == "red" and "blue" or "red"
    local rname = "my_first_mod:brick_" .. roof_color

    -- 地基
    for x = -3, 3 do
        for z = -3, 3 do
            minetest.set_node({x = pos.x + x, y = pos.y, z = pos.z + z}, {name = "my_first_mod:brick_plate"})
        end
    end

    -- 墙壁
    for y = 1, 3 do
        for x = -3, 3 do
            -- 前后墙
            minetest.set_node({x = pos.x + x, y = pos.y + y, z = pos.z - 3}, {name = bname})
            minetest.set_node({x = pos.x + x, y = pos.y + y, z = pos.z + 3}, {name = bname})
        end
        for z = -2, 2 do
            -- 左右墙
            minetest.set_node({x = pos.x - 3, y = pos.y + y, z = pos.z + z}, {name = bname})
            minetest.set_node({x = pos.x + 3, y = pos.y + y, z = pos.z + z}, {name = bname})
        end
    end

    -- 门 (正面中间)
    minetest.set_node({x = pos.x, y = pos.y + 1, z = pos.z - 3}, {name = "air"})
    minetest.set_node({x = pos.x, y = pos.y + 2, z = pos.z - 3}, {name = "air"})

    -- 窗户改用白色积木
    minetest.set_node({x = pos.x - 2, y = pos.y + 2, z = pos.z - 3}, {name = B.white})
    minetest.set_node({x = pos.x + 2, y = pos.y + 2, z = pos.z - 3}, {name = B.white})
    minetest.set_node({x = pos.x - 3, y = pos.y + 2, z = pos.z + 1}, {name = B.white})
    minetest.set_node({x = pos.x + 3, y = pos.y + 2, z = pos.z + 1}, {name = B.white})

    -- 屋顶
    for x = -3, 3 do
        for z = -3, 3 do
            minetest.set_node({x = pos.x + x, y = pos.y + 4, z = pos.z + z}, {name = rname})
        end
    end

    -- 室内灯
    minetest.set_node({x = pos.x, y = pos.y + 3, z = pos.z}, {name = "my_first_mod:brick_glow"})

    -- 地板
    for x = -2, 2 do
        for z = -2, 2 do
            minetest.set_node({x = pos.x + x, y = pos.y + 1, z = pos.z + z}, {name = "my_first_mod:brick_white"})
        end
    end
end

local function build_lamppost(pos)
    -- 路灯柱
    for y = 1, 3 do
        minetest.set_node({x = pos.x, y = pos.y + y, z = pos.z}, {name = "my_first_mod:brick_gray"})
    end
    -- 灯
    minetest.set_node({x = pos.x, y = pos.y + 4, z = pos.z}, {name = "my_first_mod:brick_glow"})
end

local function build_village(center)
    local colors = {"red", "blue", "yellow", "green", "orange"}
    local houses = 0

    -- 生成3-5栋房屋
    local num_houses = math.random(3, 5)
    for i = 1, num_houses do
        local angle = (i / num_houses) * math.pi * 2
        local dist = math.random(10, 16)
        local hpos = {
            x = center.x + math.cos(angle) * dist,
            y = center.y,
            z = center.z + math.sin(angle) * dist,
        }
        -- 找地面
        for dy = -5, 5 do
            local node = minetest.get_node_or_nil({x = hpos.x, y = hpos.y + dy, z = hpos.z})
            local def = node and minetest.registered_nodes[node.name]
            if def and def.walkable and node.name ~= "air" then
                hpos.y = hpos.y + dy
                break
            end
        end

        build_house(hpos, colors[(i % #colors) + 1])
        houses = houses + 1

        -- 路灯
        build_lamppost({x = hpos.x + 4, y = hpos.y, z = hpos.z + 4})
    end

    -- 中心广场
    for x = -2, 2 do
        for z = -2, 2 do
            minetest.set_node({x = center.x + x, y = center.y, z = center.z + z}, {name = "my_first_mod:brick_white"})
        end
    end
    -- 中心发光柱
    minetest.set_node({x = center.x, y = center.y + 1, z = center.z}, {name = "my_first_mod:brick_glow"})
    minetest.set_node({x = center.x, y = center.y + 2, z = center.z}, {name = "my_first_mod:brick_glow"})

    return houses
end

-- 生成村庄命令
minetest.register_chatcommand("village", {
    description = "在当前位置生成乐高村庄",
    func = function(name, param)
        local player = minetest.get_player_by_name(name)
        if not player then return false, "玩家不存在" end
        local pos = player:get_pos()
        pos.y = math.floor(pos.y)

        -- 找地面
        for dy = -3, 3 do
            local node = minetest.get_node_or_nil({x = pos.x, y = pos.y + dy, z = pos.z})
            local def = node and minetest.registered_nodes[node.name]
            if def and def.walkable and node.name ~= "air" then
                pos.y = pos.y + dy
                break
            end
        end

        local count = build_village(pos)
        return true, string.format("乐高村庄已生成！包含 %d 栋房屋和 %d 个村民", count, count)
    end,
})

-- 随机生成村庄（探索时触发）
local village_gen_timer = 0
local generated_villages = {}
minetest.register_globalstep(function(dtime)
    village_gen_timer = village_gen_timer + dtime
    if village_gen_timer < 120 then return end
    village_gen_timer = 0

    for _, player in ipairs(minetest.get_connected_players()) do
        local ppos = player:get_pos()

        -- 检查是否已有村庄在附近
        local too_close = false
        for _, vpos in ipairs(generated_villages) do
            if vector.distance(ppos, vpos) < 100 then
                too_close = true
                break
            end
        end
        if too_close then goto continue end

        -- 5% 概率生成
        if math.random(1, 20) > 1 then goto continue end

        -- 找合适的平地
        local angle = math.random() * math.pi * 2
        local dist = math.random(30, 60)
        local vpos = {
            x = math.floor(ppos.x + math.cos(angle) * dist),
            y = math.floor(ppos.y),
            z = math.floor(ppos.z + math.sin(angle) * dist),
        }

        -- 检查地面
        local node = minetest.get_node_or_nil(vpos)
        if not node then goto continue end
        local def = minetest.registered_nodes[node.name]
        if not def or not def.walkable then goto continue end

        build_village(vpos)
        table.insert(generated_villages, vpos)
        minetest.chat_send_player(player:get_player_name(), "§e发现了一个乐高村庄！")

        ::continue::
    end
end)

-- ============================================================
-- 12. 乐高上海城市
-- ============================================================

local B = {}  -- 快捷方块名
for _, c in ipairs({"red","blue","yellow","green","white","black","orange","purple","lime","cyan","pink","gray"}) do
    B[c] = "my_first_mod:brick_" .. c
end
B.glow = "my_first_mod:brick_glow"
B.clear = "my_first_mod:brick_white"  -- 透明积木改用白色
B.plate = "my_first_mod:brick_plate"

-- 辅助：填充长方体
local function fill_box(pos, sx, sy, sz, ex, ey, ez, node_name)
    for x = sx, ex do
        for y = sy, ey do
            for z = sz, ez do
                minetest.set_node({x = pos.x + x, y = pos.y + y, z = pos.z + z}, {name = node_name})
            end
        end
    end
end

-- 辅助：填充空心长方体（只有外壳）
local function fill_shell(pos, sx, sy, sz, ex, ey, ez, node_name)
    for x = sx, ex do
        for y = sy, ey do
            for z = sz, ez do
                if x == sx or x == ex or y == sy or y == ey or z == sz or z == ez then
                    minetest.set_node({x = pos.x + x, y = pos.y + y, z = pos.z + z}, {name = node_name})
                else
                    minetest.set_node({x = pos.x + x, y = pos.y + y, z = pos.z + z}, {name = "air"})
                end
            end
        end
    end
end

-- 辅助：圆柱体
local function fill_cylinder(pos, cx, cy, cz, radius, height, node_name)
    for y = 0, height - 1 do
        for x = -radius, radius do
            for z = -radius, radius do
                if x * x + z * z <= radius * radius then
                    minetest.set_node({x = pos.x + cx + x, y = pos.y + cy + y, z = pos.z + cz + z}, {name = node_name})
                end
            end
        end
    end
end

-- 辅助：球体
local function fill_sphere(pos, cx, cy, cz, radius, node_name)
    for x = -radius, radius do
        for y = -radius, radius do
            for z = -radius, radius do
                if x * x + y * y + z * z <= radius * radius then
                    minetest.set_node({x = pos.x + cx + x, y = pos.y + cy + y, z = pos.z + cz + z}, {name = node_name})
                end
            end
        end
    end
end

-- ---------- 东方明珠塔 ----------
local function build_oriental_pearl(pos)
    -- 三脚架基座
    for y = 0, 5 do
        for _, angle in ipairs({0, 2.094, 4.189}) do
            local rx = math.cos(angle) * 3
            local rz = math.sin(angle) * 3
            fill_box(pos, math.floor(rx), y, math.floor(rz), math.ceil(rx), y, math.ceil(rz), B.pink)
        end
    end
    -- 主柱
    fill_cylinder(pos, 0, 0, 0, 2, 35, B.pink)
    -- 第一个大球（低球）
    fill_sphere(pos, 0, 18, 0, 5, B.purple)
    fill_sphere(pos, 0, 18, 0, 4, B.glow)
    -- 连接柱
    fill_cylinder(pos, 0, 23, 0, 1, 12, B.pink)
    -- 第二个小球（高球）
    fill_sphere(pos, 0, 33, 0, 4, B.purple)
    fill_sphere(pos, 0, 33, 0, 3, B.glow)
    -- 尖顶天线
    fill_cylinder(pos, 0, 37, 0, 1, 15, B.gray)
    -- 顶灯
    minetest.set_node({x = pos.x, y = pos.y + 52, z = pos.z}, {name = B.glow})
    -- 塔基灯光
    fill_box(pos, -4, 0, -4, 4, 0, 4, B.plate)
end

-- ---------- 上海中心大厦 (632m, 螺旋形) ----------
local function build_shanghai_tower(pos)
    -- 基座
    fill_box(pos, -5, 0, -5, 5, 2, 5, B.gray)
    -- 主塔体（逐层螺旋收窄）
    local max_h = 60
    for y = 3, max_h do
        local t = (y - 3) / (max_h - 3)
        local radius = math.floor(5 - t * 2 + 0.5)
        if radius < 2 then radius = 2 end
        -- 螺旋偏移
        local offset = math.floor(y * 0.3)
        for x = -radius, radius do
            for z = -radius, radius do
                local dist = math.sqrt(x * x + z * z)
                if dist <= radius and dist >= radius - 1 then
                    local color = (y + offset) % 3 == 0 and B.cyan or B.white
                    if (y + offset) % 5 == 0 then color = B.blue end
                    minetest.set_node({x = pos.x + x, y = pos.y + y, z = pos.z + z}, {name = color})
                elseif dist < radius - 1 then
                    if y % 4 == 0 then
                        minetest.set_node({x = pos.x + x, y = pos.y + y, z = pos.z + z}, {name = B.clear})
                    else
                        minetest.set_node({x = pos.x + x, y = pos.y + y, z = pos.z + z}, {name = "air"})
                    end
                end
            end
        end
    end
    -- 顶部尖塔
    fill_cylinder(pos, 0, max_h, 0, 1, 8, B.cyan)
    minetest.set_node({x = pos.x, y = pos.y + max_h + 8, z = pos.z}, {name = B.glow})
end

-- ---------- 金茂大厦 (420m, 宝塔风格) ----------
local function build_jinmao(pos)
    -- 基座
    fill_box(pos, -4, 0, -4, 4, 2, 4, B.gray)
    -- 宝塔式逐层收窄
    local sections = {
        {y0 = 3,  y1 = 12, r = 4,  color = B.orange},
        {y0 = 13, y1 = 20, r = 3,  color = B.yellow},
        {y0 = 21, y1 = 28, r = 3,  color = B.orange},
        {y0 = 29, y1 = 34, r = 2,  color = B.yellow},
        {y0 = 35, y1 = 40, r = 2,  color = B.orange},
        {y0 = 41, y1 = 44, r = 1,  color = B.yellow},
    }
    for _, sec in ipairs(sections) do
        for y = sec.y0, sec.y1 do
            for x = -sec.r, sec.r do
                for z = -sec.r, sec.r do
                    if math.abs(x) <= sec.r and math.abs(z) <= sec.r then
                        if math.abs(x) == sec.r or math.abs(z) == sec.r then
                            minetest.set_node({x = pos.x + x, y = pos.y + y, z = pos.z + z}, {name = sec.color})
                        elseif y == sec.y0 or y == sec.y1 then
                            minetest.set_node({x = pos.x + x, y = pos.y + y, z = pos.z + z}, {name = sec.color})
                        else
                            minetest.set_node({x = pos.x + x, y = pos.y + y, z = pos.z + z}, {name = B.clear})
                        end
                    end
                end
            end
        end
    end
    -- 尖顶
    fill_cylinder(pos, 0, 45, 0, 1, 6, B.gray)
    minetest.set_node({x = pos.x, y = pos.y + 51, z = pos.z}, {name = B.glow})
end

-- ---------- 环球金融中心 (492m, 开瓶器) ----------
local function build_world_financial(pos)
    -- 基座
    fill_box(pos, -4, 0, -4, 4, 2, 4, B.gray)
    -- 主塔（方形，向上收窄）
    for y = 3, 45 do
        local t = (y - 3) / 42
        local r = math.floor(4 - t * 1.5 + 0.5)
        if r < 2 then r = 2 end
        fill_shell(pos, -r, y, -r, r, y, r, B.white)
    end
    -- 顶部缺口（开瓶器造型）
    for y = 40, 48 do
        -- 挖一个方形洞
        for x = -2, 2 do
            for z = -2, 2 do
                minetest.set_node({x = pos.x + x, y = pos.y + y, z = pos.z + z}, {name = "air"})
            end
        end
        -- 保留外围框架
        local r = 2
        for x = -3, 3 do
            for z = -3, 3 do
                if math.abs(x) == 3 or math.abs(z) == 3 then
                    minetest.set_node({x = pos.x + x, y = pos.y + y, z = pos.z + z}, {name = B.blue})
                end
            end
        end
    end
    -- 天线
    fill_cylinder(pos, 0, 49, 0, 1, 4, B.gray)
    minetest.set_node({x = pos.x, y = pos.y + 53, z = pos.z}, {name = B.glow})
end

-- ---------- 外滩建筑群 ----------
local function build_bund(pos)
    local bund_buildings = {
        -- {offset_x, width, depth, height, color, roof_color, name}
        {0,  7, 5, 12, B.gray,  B.red,   "海关大楼"},
        {9,  6, 5, 10, B.yellow, B.red,   "汇丰银行"},
        {17, 5, 5, 8,  B.white,  B.blue,  "和平饭店"},
        {24, 6, 5, 11, B.orange, B.gray,  "中国银行"},
        {32, 5, 4, 7,  B.pink,  B.purple,"外滩18号"},
        {39, 7, 5, 9,  B.green, B.red,    "友邦大厦"},
        {48, 5, 4, 8,  B.cyan,  B.gray,   "外滩中心"},
    }

    for _, b in ipairs(bund_buildings) do
        local bx, bw, bd, bh, bc, br = b[1], b[2], b[3], b[4], b[5], b[6]
        -- 建筑
        fill_shell(pos, bx, 0, 0, bx + bw, bh, bd, bc)
        -- 屋顶
        fill_box(pos, bx, bh + 1, 0, bx + bw, bh + 1, bd, br)
        -- 窗户（每隔2层放透明积木）
        for y = 2, bh - 1, 2 do
            for x = bx + 1, bx + bw - 1 do
                minetest.set_node({x = pos.x + x, y = pos.y + y, z = pos.z}, {name = B.clear})
            end
        end
        -- 内部灯光
        minetest.set_node({x = pos.x + bx + math.floor(bw / 2), y = pos.y + 1, z = pos.z + math.floor(bd / 2)}, {name = B.glow})
    end
end

-- ---------- 黄浦江 ----------
local function build_river(pos, length, width)
    for x = 0, length do
        for z = -width, width do
            -- 挖深一层填水
            minetest.set_node({x = pos.x + x, y = pos.y, z = pos.z + z}, {name = "default:water_source"})
            minetest.set_node({x = pos.x + x, y = pos.y - 1, z = pos.z + z}, {name = "default:water_source"})
        end
    end
end

-- ---------- 南浦大桥 ----------
local function build_bridge(pos, length)
    -- 桥面
    for x = 0, length do
        minetest.set_node({x = pos.x + x, y = pos.y + 8, z = pos.z - 3}, {name = B.gray})
        minetest.set_node({x = pos.x + x, y = pos.y + 8, z = pos.z - 2}, {name = B.gray})
        minetest.set_node({x = pos.x + x, y = pos.y + 8, z = pos.z - 1}, {name = B.gray})
        minetest.set_node({x = pos.x + x, y = pos.y + 8, z = pos.z}, {name = B.gray})
        minetest.set_node({x = pos.x + x, y = pos.y + 8, z = pos.z + 1}, {name = B.gray})
        minetest.set_node({x = pos.x + x, y = pos.y + 8, z = pos.z + 2}, {name = B.gray})
        minetest.set_node({x = pos.x + x, y = pos.y + 8, z = pos.z + 3}, {name = B.gray})
    end
    -- 两个桥塔
    for _, tx in ipairs({0, length}) do
        fill_box(pos, tx, 0, -4, tx, 7, 4, B.red)
        -- 斜拉索
        for x = tx - 6, tx + 6 do
            if x >= 0 and x <= length and x ~= tx then
                local dy = 8 - math.abs(x - tx)
                if dy > 0 then
                    minetest.set_node({x = pos.x + x, y = pos.y + dy, z = pos.z}, {name = B.yellow})
                end
            end
        end
    end
end

-- ---------- 邱明 标志牌 ----------
local function build_qiuming_sign(pos)
    -- Qm 两字, 7宽x9高, scale=4
    local letters = {
        Q = {
            ".#####.",
            "#.....#",
            "#.....#",
            "#.....#",
            "#.#...#",
            "#..#..#",
            "#...#.#",
            ".#####.",
            "...#...",
        },
        m = {
            "#......",
            "#......",
            "#......",
            "##...##",
            "#.#.#.#",
            "#.#.#.#",
            "#..#..#",
            "#.....#",
            "#.....#",
        },
    }

    local bg = B.white
    local fg = B.red
    local glow = B.glow
    local scale = 4

    local line = {"Q", "m"}
    local lw = 7
    local lh = 9
    local gap = 2
    local total_letters_w = #line * lw + (#line - 1) * gap
    local total_h = (lh + 4) * scale
    local total_w = (total_letters_w + 4) * scale

    local bx = -math.floor(total_w / 2)
    local by = 3

    -- 背景板
    fill_box(pos, bx - 2, by - 2, 0, bx + total_w + 1, by + total_h + 1, 0, bg)

    -- 边框发光
    for x = bx - 2, bx + total_w + 1 do
        minetest.set_node({x = pos.x + x, y = pos.y + by - 2, z = pos.z}, {name = glow})
        minetest.set_node({x = pos.x + x, y = pos.y + by + total_h + 1, z = pos.z}, {name = glow})
    end
    for y = by - 2, by + total_h + 1 do
        minetest.set_node({x = pos.x + bx - 2, y = pos.y + y, z = pos.z}, {name = glow})
        minetest.set_node({x = pos.x + bx + total_w + 1, y = pos.y + y, z = pos.z}, {name = glow})
    end

    -- 画字母 (正面 z, 背面 z-1 镜像)
    local function draw_letter(letter, x_start, y_start, z_off)
        local pattern = letters[letter]
        if not pattern then return end
        for row = 1, lh do
            local line_str = pattern[row]
            for col = 1, lw do
                if line_str:sub(col, col) == "#" then
                    local px = x_start + (col - 1) * scale
                    local py = y_start + (lh - row) * scale
                    for dx = 0, scale - 1 do
                        for dy = 0, scale - 1 do
                            -- 正面
                            minetest.set_node({x = pos.x + px + dx, y = pos.y + py + dy, z = pos.z + z_off}, {name = fg})
                        end
                    end
                end
            end
        end
    end

    -- 画正面 Qm (z=0)
    local x_off = bx + 2 * scale
    for li, letter in ipairs(line) do
        draw_letter(letter, x_off + (li - 1) * (lw + gap) * scale, by + 2 * scale, 0)
    end

    -- 画背面 mQ 镜像 (z=-1, 字母顺序反转 + 像素镜像)
    local x_off_back = bx + 2 * scale
    for li = #line, 1, -1 do
        local letter = line[li]
        local pattern = letters[letter]
        if pattern then
            for row = 1, lh do
                local line_str = pattern[row]
                for col = 1, lw do
                    if line_str:sub(col, col) == "#" then
                        local px = x_off_back + (#line - li) * (lw + gap) * scale + (lw - col) * scale
                        local py = by + 2 * scale + (lh - row) * scale
                        for dx = 0, scale - 1 do
                            for dy = 0, scale - 1 do
                                minetest.set_node({x = pos.x + px + dx, y = pos.y + py + dy, z = pos.z - 1}, {name = fg})
                            end
                        end
                    end
                end
            end
        end
    end

    -- 支柱
    fill_cylinder(pos, bx + 4, 0, 0, 1, 2, B.gray)
    fill_cylinder(pos, bx + total_w - 5, 0, 0, 1, 2, B.gray)
end

-- ---------- 主生成函数 ----------
local shanghai_center = nil  -- 记录已生成的上海中心点
local shanghai_player = nil

local function build_shanghai(center)
    minetest.chat_send_player(center.player, "§e正在建造乐高上海... 请稍候")

    local pos = {x = center.x, y = center.y, z = center.z}
    local pname = center.player
    shanghai_center = {x = pos.x, y = pos.y, z = pos.z}
    shanghai_player = pname

    -- 0. 先清空整个区域（扩大范围，确保覆盖所有建筑）
    for x = -60, 60 do
        for y = -5, 80 do
            for z = -70, 70 do
                minetest.set_node({x = pos.x + x, y = pos.y + y, z = pos.z + z}, {name = "air"})
            end
        end
    end

    -- 1. 地基平整
    for x = -50, 50 do
        for z = -60, 60 do
            minetest.set_node({x = pos.x + x, y = pos.y, z = pos.z + z}, {name = B.plate})
        end
    end

    -- 2. 黄浦江（南北贯穿）
    build_river({x = pos.x + 20, y = pos.y, z = pos.z - 50}, 100, 6)

    -- 3. 浦东侧（江东）
    -- 东方明珠塔
    build_oriental_pearl({x = pos.x + 30, y = pos.y + 1, z = pos.z - 20})

    -- 上海中心大厦
    build_shanghai_tower({x = pos.x + 38, y = pos.y + 1, z = pos.z - 5})

    -- 金茂大厦
    build_jinmao({x = pos.x + 32, y = pos.y + 1, z = pos.z + 5})

    -- 环球金融中心
    build_world_financial({x = pos.x + 44, y = pos.y + 1, z = pos.z + 2})

    -- 4. 浦西侧（江西）- 外滩建筑群
    build_bund({x = pos.x - 35, y = pos.y + 1, z = pos.z - 30})

    -- 5. 南浦大桥（跨江）
    build_bridge({x = pos.x + 20, y = pos.y + 1, z = pos.z - 45}, 40)

    -- 6. 路灯
    for x = -40, 40, 8 do
        build_lamppost({x = pos.x + x, y = pos.y, z = pos.z - 12})
        build_lamppost({x = pos.x + x, y = pos.y, z = pos.z + 12})
    end

    -- 8. 广场中心标志
    minetest.set_node({x = pos.x, y = pos.y + 1, z = pos.z}, {name = B.glow})
    minetest.set_node({x = pos.x, y = pos.y + 2, z = pos.z}, {name = B.glow})

    -- 9. 文字招牌 "我们只能看到我们看到的世界"
    -- 用英文 WE SEE WHAT WE SEE, 大号字, 每个像素2x2
    local sign_pos = {x = pos.x, y = pos.y + 1, z = pos.z + 20}
    -- 背景板 (大)
    fill_box(sign_pos, -30, 0, 0, 30, 20, 0, B.red)
    -- 内层白色板
    fill_box(sign_pos, -28, 1, 0, 28, 19, 0, B.white)
    -- 发光边框
    for x = -31, 31 do
        minetest.set_node({x = sign_pos.x + x, y = sign_pos.y, z = sign_pos.z}, {name = B.glow})
        minetest.set_node({x = sign_pos.x + x, y = sign_pos.y + 21, z = sign_pos.z}, {name = B.glow})
    end
    for y = 0, 21 do
        minetest.set_node({x = sign_pos.x - 31, y = sign_pos.y + y, z = sign_pos.z}, {name = B.glow})
        minetest.set_node({x = sign_pos.x + 31, y = sign_pos.y + y, z = sign_pos.z}, {name = B.glow})
    end
    -- 支柱
    fill_box(sign_pos, -15, -4, 0, -14, 0, 0, B.gray)
    fill_box(sign_pos, 14, -4, 0, 15, 0, 0, B.gray)

    -- 大号字母 5x7, 每像素2x2
    local scale = 2
    local chars = {
        W = {".#.#.","#.#.#","#.#.#","#.#.#","#####","#...#","#...#"},
        E = {"#####","#....","#....","#####","#....","#....","#####"},
        S = {".###.","#....","#....",".###.","....#","#....",".###."},
        A = {".#...","#.#..","#.#..","#####","#...#","#...#","#...#"},
        H = {"#...#","#...#","#...#","#####","#...#","#...#","#...#"},
        T = {"#####","..#..","..#..","..#..","..#..","..#..","..#.."},
    }
    -- 三行文字, 每行间隔足够
    local text_lines = {"WE", "SEE", "WHAT", "WE", "SEE"}
    local ty = 2
    for li, word in ipairs(text_lines) do
        local word_w = #word * 5 * scale + (#word - 1) * scale
        local wx = -math.floor(word_w / 2)
        for ci = 1, #word do
            local ch = word:sub(ci, ci)
            local pattern = chars[ch]
            if pattern then
                for row = 1, 7 do
                    local line_str = pattern[row]
                    for col = 1, 5 do
                        if line_str:sub(col, col) == "#" then
                            for dx = 0, scale - 1 do
                                for dy = 0, scale - 1 do
                                    minetest.set_node({
                                        x = sign_pos.x + wx + (col - 1) * scale + dx,
                                        y = sign_pos.y + ty + (7 - row) * scale + dy,
                                        z = sign_pos.z
                                    }, {name = B.black})
                                end
                            end
                        end
                    end
                end
            end
            wx = wx + 6 * scale
        end
        ty = ty + 9 * scale  -- 行间距
    end

    minetest.chat_send_player(pname, "§a乐高上海建造完成！招牌: WE SEE WHAT WE SEE")

    -- 10. Qiu M 落款 (招牌右下角蓝色小字)
    local qm_pos = {x = sign_pos.x + 14, y = sign_pos.y + 15, z = sign_pos.z}
    local qm_chars = {
        Q = {".###.","#...#","#...#","#...#","#.#.#","#..#.",".###."},
        m = {"#....","#....","#....","##..#","#.#.#","#.#.#","#...#"},
    }
    local qm_scale = 2
    local qm_text = {"Q", "m"}
    local qx = 0
    for ci = 1, #qm_text do
        local ch = qm_text[ci]
        local pattern = qm_chars[ch]
        if pattern then
            for row = 1, 7 do
                local line_str = pattern[row]
                for col = 1, 5 do
                    if line_str:sub(col, col) == "#" then
                        for dx = 0, qm_scale - 1 do
                            for dy = 0, qm_scale - 1 do
                                minetest.set_node({
                                    x = qm_pos.x + qx + (col - 1) * qm_scale + dx,
                                    y = qm_pos.y + (7 - row) * qm_scale + dy,
                                    z = qm_pos.z
                                }, {name = B.blue})
                            end
                        end
                    end
                end
            end
        end
        qx = qx + 6 * qm_scale
    end
end

-- 生成命令（异步分步执行避免卡顿）
minetest.register_chatcommand("shanghai", {
    description = "建造乐高上海（如已存在则重建原位）",
    func = function(name, param)
        local player = minetest.get_player_by_name(name)
        if not player then return false, "玩家不存在" end
        local pos
        -- 如果已有建筑，在原位重建
        if shanghai_center then
            pos = {x = shanghai_center.x, y = shanghai_center.y, z = shanghai_center.z}
        else
            pos = player:get_pos()
            pos.y = math.floor(pos.y)
            for dy = -3, 3 do
                local node = minetest.get_node_or_nil({x = pos.x, y = pos.y + dy, z = pos.z})
                local def = node and minetest.registered_nodes[node.name]
                if def and def.walkable and node.name ~= "air" then
                    pos.y = pos.y + dy
                    break
                end
            end
        end
        pos.player = name
        minetest.after(0, build_shanghai, pos)
        return true, "开始建造乐高上海..."
    end,
})

-- /reload_shanghai: 重新加载 mod 后自动刷新建筑（保留原位置）
minetest.register_chatcommand("reload_shanghai", {
    description = "在原位重新生成乐高上海（清空后重建）",
    func = function(name, param)
        if not shanghai_center then
            return false, "尚未生成过上海，请先用 /shanghai"
        end
        local pos = {x = shanghai_center.x, y = shanghai_center.y, z = shanghai_center.z, player = name}
        minetest.after(0, build_shanghai, pos)
        return true, "正在原位重建乐高上海..."
    end,
})

-- /clean_all: 清除世界中所有乐高积木方块（保留最后一次上海位置，之后可用 /shanghai 重建）
minetest.register_chatcommand("clean_all", {
    description = "清除世界中所有乐高积木方块",
    func = function(name, param)
        local player = minetest.get_player_by_name(name)
        if not player then return false, "玩家不存在" end
        local ppos = player:get_pos()

        -- 收集所有 brick 节点名
        local brick_names = {}
        for _, c in ipairs({"red","blue","yellow","green","white","black","orange","purple","lime","cyan","pink","gray"}) do
            table.insert(brick_names, "my_first_mod:brick_" .. c)
        end
        table.insert(brick_names, "my_first_mod:brick_glow")
        table.insert(brick_names, "my_first_mod:brick_clear")
        table.insert(brick_names, "my_first_mod:brick_plate")

        local count = 0
        -- 分块扫描，避免一次性扫描过大区域卡死
        for cx = ppos.x - 200, ppos.x + 200, 80 do
            for cz = ppos.z - 200, ppos.z + 200, 80 do
                for cy = ppos.y - 20, ppos.y + 80, 40 do
                    local pos1 = {x = cx, y = cy, z = cz}
                    local pos2 = {x = cx + 79, y = cy + 39, z = cz + 79}
                    local found = minetest.find_nodes_in_area(pos1, pos2, brick_names)
                    for _, fpos in ipairs(found) do
                        minetest.set_node(fpos, {name = "air"})
                        count = count + 1
                    end
                end
            end
        end

        -- 清除村民
        for _, obj in ipairs(minetest.get_objects_inside_radius(ppos, 300)) do
            local ent = obj:get_luaentity()
            if ent and ent.name == "my_first_mod:villager" then
                obj:remove()
            end
        end

        -- 重置上海中心（需要重新生成）
        shanghai_center = nil

        minetest.chat_send_player(name, string.format("已清除 %d 个乐高积木方块，可重新用 /shanghai 生成", count))
        return true
    end,
})

-- /undo: 撤销最近的 /build 生成 (清除前方区域的非自然方块)
minetest.register_chatcommand("undo", {
    description = "撤销最近的建筑（清除前方方块）",
    func = function(name, param)
        local player = minetest.get_player_by_name(name)
        if not player then return false, "玩家不存在" end
        local pos = player:get_pos()
        local dir = player:get_look_dir()
        -- 建筑在前方15格，清除前方区域
        local cx = pos.x + math.floor(dir.x * 15)
        local cz = pos.z + math.floor(dir.z * 15)
        local r = 30
        local count = 0

        -- 自然方块不清除
        local natural = {
            ["air"] = true, ["default:dirt_with_grass"] = true,
            ["default:dirt"] = true, ["default:stone"] = true,
            ["default:sand"] = true, ["default:desert_sand"] = true,
            ["default:desert_stone"] = true, ["default:water_source"] = true,
            ["default:water_flowing"] = true, ["default:tree"] = true,
            ["default:leaves"] = true, ["default:cobble"] = true,
            ["default:snow"] = true, ["default:ice"] = true,
            ["default:clay"] = true, ["default:sandstone"] = true,
            ["default:gravel"] = true, ["default:papyrus"] = true,
            ["default:junglegrass"] = true, ["default:jungletree"] = true,
            ["default:jungleleaves"] = true, ["default:pine_tree"] = true,
            ["default:pine_needles"] = true, ["default:bush_stem"] = true,
            ["default:grass_1"] = true, ["default:grass_2"] = true,
            ["default:grass_3"] = true, ["default:grass_4"] = true,
            ["default:grass_5"] = true, ["default:dry_grass_1"] = true,
            ["default:dry_shrub"] = true, ["default:cactus_top"] = true,
            ["default:cactus_side"] = true, ["default:apple"] = true,
            ["default:flowers:rose"] = true, ["flowers:rose"] = true,
            ["flowers:tulip"] = true, ["flowers:dandelion_yellow"] = true,
            ["flowers:geranium"] = true, ["flowers:dandelion_white"] = true,
            ["default:dry_dirt"] = true, ["default:permafrost"] = true,
            ["mapgen_stone"] = true, ["mapgen_dirt"] = true,
            ["mapgen_water_source"] = true, ["mapgen_river_water_source"] = true,
            ["default:stone_with_coal"] = true, ["default:stone_with_iron"] = true,
            ["default:stone_with_copper"] = true, ["default:stone_with_gold"] = true,
            ["default:stone_with_diamond"] = true, ["default:stone_with_mese"] = true,
            ["default:stone_with_tin"] = true, ["default:coalblock"] = true,
        }

        for x = cx - r, cx + r do
            for y = 1, 80 do
                for z = cz - r, cz + r do
                    local node = minetest.get_node_or_nil({x=x, y=pos.y + y, z=z})
                    if node and node.name ~= "air" and not natural[node.name] then
                        minetest.set_node({x=x, y=pos.y + y, z=z}, {name="air"})
                        count = count + 1
                    end
                end
            end
        end

        -- 也清除地面层填的石头（/build 填的）
        for x = cx - r, cx + r do
            for z = cz - r, cz + r do
                local node = minetest.get_node_or_nil({x=x, y=pos.y, z=z})
                if node and node.name == "default:stone" then
                    -- 检查是否原本是水或空气
                    local below = minetest.get_node_or_nil({x=x, y=pos.y-1, z=z})
                    if below and (below.name == "default:water_source" or below.name == "default:water_flowing" or below.name == "air") then
                        minetest.set_node({x=x, y=pos.y, z=z}, {name="default:water_source"})
                        count = count + 1
                    end
                end
            end
        end

        minetest.chat_send_player(name, string.format("已撤销 %d 个方块", count))
        return true
    end,
})

-- ============================================================
-- 大小写不敏感命令 (修复 macOS Caps Lock 导致 /BUILD 无法执行)
-- ============================================================
minetest.register_on_chatcommand(function(name, cmd, param)
    local lower_cmd = cmd:lower()
    if lower_cmd ~= cmd then
        -- 命令包含大写，查找小写版本
        local cmd_def = minetest.registered_chatcommands[lower_cmd]
        if cmd_def then
            -- 执行小写版本的命令
            local has_privs, missing_privs = minetest.check_player_privs(name, cmd_def.privs)
            if has_privs then
                local success, result = cmd_def.func(name, param)
                if result then
                    minetest.chat_send_player(name, result)
                end
            else
                minetest.chat_send_player(name, "权限不足: " .. table.concat(missing_privs, ", "))
            end
            return true  -- 阻止默认处理(避免报错)
        end
    end
    -- 不拦截正常小写命令
    return false
end)

print("[my_first_mod] Mod 加载完成！（饥饿+生物+乐高风格+积木+NPC村庄+上海城市）")
