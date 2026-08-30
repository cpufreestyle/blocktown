-- ai_town/init.lua
-- AI 小镇 v6: 极简对话 + 流畅NPC + 精美建筑 + 性能优化

-- ============================================================
-- 配置
-- ============================================================
local AI_CONFIG = {
    -- API Key 从 minetest.conf 的 stepfun_api_key 设置读取 (不写入源码)
    api_key = minetest.settings:get("stepfun_api_key") or "",
    base_url = "https://api.stepfun.com/v1/chat/completions",
    model = "step-3.5-flash",
    max_history = 6,
    max_memories = 20,
}

local HTTP_API = minetest.request_http_api()

-- ============================================================
-- NPC 定义
-- ============================================================
local NPC_TYPES = {
    {name="baker", display="面包师老王", color="#FFD700",
     system_prompt="你是面包师老王，乐高小镇面包店老板。热情开朗，爱聊烘焙。回复简短(50字内)，中文。",
     work_pos={x=-9,y=1,z=-4}, home_pos={x=-6,y=1,z=4}, walk_pos={x=0,y=1,z=0},
     quest_item="default:apple", quest_count=5, quest_desc="帮我收集5个苹果做苹果派",
     liked_item="my_first_mod:bread", liked_desc="面包",
     shop={{"my_first_mod:bread","面包",2},{"my_first_mod:apple","苹果",1}}},
    {name="scholar", display="学者李书生", color="#87CEEB",
     system_prompt="你是学者李书生，住图书馆旁。博学多才，说话文绉绉，爱引古诗词。回复简短(50字内)，中文带文言。",
     work_pos={x=9,y=1,z=-4}, home_pos={x=-10,y=1,z=4}, walk_pos={x=0,y=1,z=-2},
     quest_item="default:book", quest_count=1, quest_desc="我丢了本书，帮我找找",
     liked_item="my_first_mod:brick_cyan", liked_desc="青色积木(墨色)",
     shop={}},
    {name="merchant", display="商人钱掌柜", color="#FF6347",
     system_prompt="你是商人钱掌柜，市场摆摊。精明诚信，爱推销。回复简短(50字内)，中文。",
     work_pos={x=8,y=1,z=4}, home_pos={x=-4,y=1,z=4}, walk_pos={x=3,y=1,z=-3},
     quest_item="my_first_mod:brick_glow", quest_count=3, quest_desc="找3个发光积木有大客户要",
     liked_item="default:gold_ingot", liked_desc="金锭",
     shop={{"my_first_mod:brick_red","红积木",1},{"my_first_mod:brick_glow","发光积木",3},{"my_first_mod:brick_wand","魔杖",5}}},
    {name="guard", display="守卫赵铁柱", color="#90EE90",
     system_prompt="你是守卫赵铁柱，负责小镇安全。正直严肃。回复简短(40字内)，中文军人风格。",
     work_pos={x=0,y=1,z=-10}, home_pos={x=10,y=1,z=4}, walk_pos={x=0,y=1,z=-4},
     quest_item="my_first_mod:brick_gray", quest_count=4, quest_desc="收集4个灰色积木修城墙",
     liked_item="my_first_mod:bread", liked_desc="面包(巡逻干粮)",
     shop={}},
    {name="healer", display="医者孙灵儿", color="#DDA0DD",
     system_prompt="你是医者孙灵儿，药铺工作。温柔善良，擅草药，会关心人。回复简短(50字内)，中文温柔语气。",
     work_pos={x=-10,y=1,z=0}, home_pos={x=-6,y=1,z=4}, walk_pos={x=-2,y=1,z=3},
     quest_item="flowers:rose", quest_count=3, quest_desc="采3朵玫瑰花做药引",
     liked_item="my_first_mod:apple", liked_desc="苹果(入药)",
     shop={{"my_first_mod:bread","养生面包",3}}},
    {name="fisher", display="渔夫周三", color="#F0E68C",
     system_prompt="你是渔夫周三，南门外河边钓鱼。豪爽直率，爱讲故事。回复简短(50字内)，中文带江湖气。",
     work_pos={x=0,y=1,z=10}, home_pos={x=6,y=1,z=4}, walk_pos={x=2,y=1,z=5},
     quest_item="default:clay_lump", quest_count=3, quest_desc="找3个黏土做鱼竿支架",
     liked_item="my_first_mod:brick_glow", liked_desc="发光积木(夜钓浮漂)",
     shop={}},
}

-- 全局状态
local npc_dialogs = {}
local npc_tasks = {}
local npc_mood = {}
local npc_relation = {}
local npc_memories = {}
local npc_reflections = {}
local npc_talk_count = {}
local npc_plans = {}          -- 每日计划 (参照论文 Planning 模块)
local active_dialog = {}
local town_center = nil
local player_coins = {}
local player_reputation = {}  -- 玩家声誉 0-100 (50 起始)
local weather = "clear"
local weather_timer = 0
local npc_chat_timer = 0

-- ============================================================
-- 小镇事件系统 (随机事件驱动全体 NPC)
-- ============================================================
local TOWN_EVENTS = {
    {id="market_fair", name="集市", announce="🎉 集市开张了！商人钱掌柜在广场支起了摊位",
     mood_delta=5, memory="镇上今天举办集市，热闹极了"},
    {id="lost_traveler", name="迷路旅人", announce="🧳 一位迷路的旅人进城了，守卫赵铁柱正在询问来意",
     mood_delta=2, memory="今天有位迷路旅人进城，大家议论纷纷"},
    {id="harvest_day", name="丰收日", announce="🌾 今天是丰收日，面包师老王烤了好多新面包",
     mood_delta=6, memory="今天是丰收日，收成很好"},
    {id="night_patrol", name="夜间巡逻", announce="🌙 守卫赵铁柱开始夜间巡逻，大家早点回家",
     mood_delta=-2, memory="今晚有夜间巡逻，小镇戒备森严"},
    {id="story_night", name="故事会", announce="📖 故事会开始！渔夫周三在河边讲起江湖传闻",
     mood_delta=4, memory="今晚河边有故事会，很多人去听"},
}
local current_event = nil    -- {id=.., name=..}
local event_timer = 0
local EVENT_INTERVAL_MIN = 180  -- 秒
local EVENT_INTERVAL_MAX = 300

local function reputation_str(rep)
    if rep >= 85 then return "德高望重" end
    if rep >= 70 then return "乐善好施" end
    if rep >= 30 then return "普通镇民" end
    return "恶名昭著"
end

local function add_reputation(pname, delta)
    local old = player_reputation[pname] or 50
    local new = math.max(0, math.min(100, old + delta))
    player_reputation[pname] = new
    -- 跨越阈值时全服广播
    if old < 70 and new >= 70 then
        minetest.chat_send_all("§d[小镇] " .. pname .. " 在镇上声望渐高，成了乐善好施的好人！")
    elseif old >= 30 and new < 30 then
        minetest.chat_send_all("§d[小镇] " .. pname .. " 声名狼藉，镇民都开始躲着他走…")
    end
end

local function trigger_event()
    local ev = TOWN_EVENTS[math.random(#TOWN_EVENTS)]
    current_event = {id=ev.id, name=ev.name}
    for _, nd in ipairs(NPC_TYPES) do
        npc_mood[nd.name] = math.max(10, math.min(100, (npc_mood[nd.name] or 50) + ev.mood_delta))
        add_memory(nd.name, ev.memory, 3)
    end
    for _, p in ipairs(minetest.get_connected_players()) do
        minetest.chat_send_player(p:get_player_name(), "§e[小镇事件] " .. ev.announce)
    end
    return ev
end

-- ============================================================
-- 记忆系统 (参照 Generative Agents 论文: recency + importance + relevance)
-- ============================================================
local function add_memory(npc_name, text, importance)
    if not npc_memories[npc_name] then npc_memories[npc_name] = {} end
    table.insert(npc_memories[npc_name], {
        time = minetest.get_timeofday(),
        access_time = minetest.get_timeofday(),  -- 最后访问时间 (recency)
        text = text,
        importance = importance or 3,  -- 1-10 重要度
    })
    while #npc_memories[npc_name] > AI_CONFIG.max_memories do table.remove(npc_memories[npc_name], 1) end
end

-- 检索函数 (recency * 0.3 + importance * 0.4 + relevance * 0.3)
local function get_memory_context(npc_name, query)
    local mems = npc_memories[npc_name] or {}
    if #mems == 0 then return "" end
    local now = minetest.get_timeofday()
    local scored = {}
    for _, m in ipairs(mems) do
        -- Recency: 指数衰减 (最近访问的记忆得分更高)
        local time_diff = math.abs(now - (m.access_time or m.time))
        if time_diff > 0.5 then time_diff = 1 - time_diff end  -- 处理昼夜循环
        local recency = math.exp(-time_diff * 5)  -- 指数衰减
        -- Importance: 直接使用存储的重要度 (1-10 → 0-1)
        local importance = m.importance / 10
        -- Relevance: 关键词匹配度
        local relevance = 0
        local word_count = 0
        for word in query:gmatch("%S+") do
            word_count = word_count + 1
            if #word > 1 and m.text:lower():find(word:lower()) then
                relevance = relevance + 1
            end
        end
        relevance = word_count > 0 and (relevance / word_count) or 0
        -- 加权总分
        local score = recency * 0.3 + importance * 0.4 + relevance * 0.3
        table.insert(scored, {mem = m, score = score})
    end
    table.sort(scored, function(a, b) return a.score > b.score end)
    -- 取 Top-3 记忆
    local result = {}
    for i = 1, math.min(3, #scored) do
        table.insert(result, scored[i].mem.text)
        scored[i].mem.access_time = now  -- 更新访问时间
    end
    local ctx = ""
    if #result > 0 then ctx = "你最近的记忆:\n- " .. table.concat(result, "\n- ") .. "\n" end
    -- 反思总结
    local ref = npc_reflections[npc_name]
    if ref then ctx = ctx .. "你的自我认知: " .. ref .. "\n" end
    -- 当前计划
    local plan = npc_plans[npc_name]
    if plan then ctx = ctx .. "你今天的计划: " .. plan .. "\n" end
    return ctx
end

local function trigger_reflection(npc_name)
    local nd = nil
    for _, def in ipairs(NPC_TYPES) do if def.name == npc_name then nd = def break end end
    if not nd then return end
    local mems = npc_memories[npc_name] or {}
    if #mems < 3 then return end
    local mem_str = ""
    for _, m in ipairs(mems) do mem_str = mem_str .. "- " .. m.text .. "\n" end
    local payload = minetest.write_json({
        model = AI_CONFIG.model,
        messages = {{role="system", content="你是" .. nd.display .. "。简洁总结。"},
                   {role="user", content="总结以下记忆(30字内):\n" .. mem_str}},
        temperature=0.5, max_tokens=100,
    })
    if not HTTP_API then return end
    HTTP_API:fetch({
        url = AI_CONFIG.base_url, method="POST", data=payload,
        extra_headers={"Content-Type: application/json", "Authorization: Bearer " .. AI_CONFIG.api_key},
        timeout=30,
    }, function(result)
        if result.code == 200 then
            local data = minetest.parse_json(result.data)
            if data and data.choices and data.choices[1] and data.choices[1].message and data.choices[1].message.content then
                npc_reflections[npc_name] = data.choices[1].message.content
            end
        end
    end)
end

-- ============================================================
-- 每日计划生成 (参照论文 Planning 模块)
-- ============================================================
local function generate_daily_plan(npc_name)
    local nd = nil
    for _, def in ipairs(NPC_TYPES) do if def.name == npc_name then nd = def break end end
    if not nd or not HTTP_API then return end
    local mem_ctx = get_memory_context(npc_name, "今天的计划")
    local time = minetest.get_timeofday()
    local time_str = time < 0.25 and "凌晨" or (time < 0.5 and "上午" or (time < 0.75 and "下午" or "夜晚"))
    local prompt = "你今天" .. time_str .. "想做什么？列出3个活动(每个10字内)用逗号分隔。"
    local payload = minetest.write_json({
        model = AI_CONFIG.model,
        messages = {
            {role="system", content=nd.system_prompt .. "\n" .. mem_ctx .. "天气:" .. weather},
            {role="user", content=prompt},
        },
        temperature=0.6, max_tokens=150,
    })
    HTTP_API:fetch({
        url = AI_CONFIG.base_url, method="POST", data=payload,
        extra_headers={"Content-Type: application/json", "Authorization: Bearer " .. AI_CONFIG.api_key},
        timeout=30,
    }, function(result)
        if result.code == 200 then
            local data = minetest.parse_json(result.data)
            if data and data.choices and data.choices[1] and data.choices[1].message and data.choices[1].message.content then
                local plan = data.choices[1].message.content
                npc_plans[npc_name] = plan
                add_memory(npc_name, "我今天的计划: " .. plan, 4)
                minetest.log("action", "[ai_town] " .. nd.display .. " 计划: " .. plan)
            end
        end
    end)
end

-- ============================================================
-- AI 对话 (异步回调)
-- ============================================================
local function call_ai(pname, system_prompt, history, user_message, mood, relation, mem_ctx, callback)
    local mood_str = mood > 75 and "开心" or (mood > 50 and "愉快" or (mood > 25 and "一般" or "不悦"))
    local rel_str = relation > 75 and "挚友" or (relation > 50 and "朋友" or (relation > 25 and "熟人" or "陌生人"))
    local full_prompt = system_prompt .. "\n心情:" .. mood_str .. " 关系:" .. rel_str .. " 天气:" .. weather .. "。"
    -- 玩家声誉 + 小镇事件 注入
    if pname and pname ~= "NPC" then
        local rep = player_reputation[pname] or 50
        full_prompt = full_prompt .. "\n这位玩家的镇上声望: " .. rep .. "(" .. reputation_str(rep) .. ")"
    end
    if current_event then
        full_prompt = full_prompt .. "\n当前小镇事件: " .. current_event.name
    end
    full_prompt = full_prompt .. "\n"
    if mem_ctx and mem_ctx ~= "" then full_prompt = full_prompt .. mem_ctx end

    local messages = {{role="system", content=full_prompt}}
    for _, msg in ipairs(history) do table.insert(messages, msg) end
    table.insert(messages, {role="user", content=user_message})

    local payload = minetest.write_json({model=AI_CONFIG.model, messages=messages, temperature=0.8, max_tokens=500})
    if not HTTP_API then
        local cb = callback
        minetest.after(0, function() if type(cb)=="function" then cb(nil, "HTTP API 不可用") end end)
        return
    end
    local cb = callback
    HTTP_API:fetch({
        url = AI_CONFIG.base_url, method="POST", data=payload,
        extra_headers={"Content-Type: application/json", "Authorization: Bearer " .. AI_CONFIG.api_key},
        timeout=30,
    }, function(result)
        if type(cb) ~= "function" then return end
        if result.code == 200 then
            local data = minetest.parse_json(result.data)
            if data and data.choices and data.choices[1] and data.choices[1].message and data.choices[1].message.content then
                cb(data.choices[1].message.content, nil)
            else cb(nil, "AI返回格式错误") end
        else cb(nil, "HTTP " .. result.code) end
    end)
end

local function fallback_reply(npc_type)
    local r = {
        baker={"尝尝黄金吐司？","面包特别香！"}, scholar={"善哉汝有何问？","书中自有黄金屋。"},
        merchant={"客官来了！","今天特价！"}, guard={"来者何人？","小镇平安。"},
        healer={"身体可好？","注意养生。"}, fisher={"钓鱼要耐心。","河里有大鱼！"},
    }
    local list = r[npc_type] or {"..."}
    return list[math.random(#list)]
end

-- ============================================================
-- NPC 间自主对话
-- ============================================================
local function npc_talk_to_npc(n1_name, n2_name)
    local nd1, nd2 = nil, nil
    for _, def in ipairs(NPC_TYPES) do
        if def.name == n1_name then nd1 = def end
        if def.name == n2_name then nd2 = def end
    end
    if not nd1 or not nd2 then return end
    local topics = {"和" .. nd2.display .. "打招呼", "问" .. nd2.display .. "最近怎样", "聊天气"}
    local topic = topics[math.random(#topics)]
    local mem_ctx = get_memory_context(n1_name, nd2.display)
    call_ai("NPC", nd1.system_prompt, {}, topic, npc_mood[n1_name] or 50, 50, mem_ctx,
        function(reply, err)
            if reply then
                add_memory(n1_name, "我和" .. nd2.display .. "聊了: " .. reply, 3)
                add_memory(n2_name, nd1.display .. "跟我说: " .. reply, 3)
                for _, p in ipairs(minetest.get_connected_players()) do
                    if town_center and vector.distance(p:get_pos(), town_center) < 40 then
                        minetest.chat_send_player(p:get_player_name(), "§7[" .. nd1.display .. " → " .. nd2.display .. "] " .. reply)
                    end
                end
            end
        end)
end

-- ============================================================
-- 粒子特效
-- ============================================================
local function spawn_particles(pos, type)
    if type == "hearts" then
        minetest.add_particlespawner({amount=6, time=1,
            minpos={x=pos.x-0.5,y=pos.y+1,z=pos.z-0.5}, maxpos={x=pos.x+0.5,y=pos.y+2,z=pos.z+0.5},
            minvel={x=0,y=1,z=0}, maxvel={x=0.5,y=2,z=0.5},
            minsize=2, maxsize=4, texture="heart.png", glow=5})
    elseif type == "sparkle" then
        minetest.add_particlespawner({amount=10, time=0.5,
            minpos={x=pos.x-1,y=pos.y,z=pos.z-1}, maxpos={x=pos.x+1,y=pos.y+2,z=pos.z+1},
            minvel={x=-2,y=2,z=-2}, maxvel={x=2,y=4,z=2},
            minacc={x=0,y=-5,z=0}, maxacc={x=0,y=-5,z=0},
            minsize=1, maxsize=3, texture="my_first_mod_brick_glow_top.png", glow=10})
    end
end

-- ============================================================
-- NPC 实体注册 (优化: 动画 + 平滑移动 + 避障)
-- ============================================================
for _, npc_def in ipairs(NPC_TYPES) do
    minetest.register_entity("ai_town:npc_" .. npc_def.name, {
        initial_properties = {
            visual="mesh", mesh="character.b3d",
            textures={"ai_town_skin_" .. npc_def.name .. ".png"},
            visual_size={x=1.0, y=1.0, z=1.0},
            collisionbox={-0.3, 0, -0.3, 0.3, 1.7, 0.3},
            physical=true, hp_max=20, stepheight=1.1,
            nametag=npc_def.display, nametag_color=npc_def.color,
            infotext="右键对话: " .. npc_def.display,
            automatic_face_movement_dir=0,
        },
        _npc_type=npc_def.name, _npc_def=npc_def,
        _timer=0, _walk_timer=0, _meet_timer=0, _stuck_timer=0, _last_pos=nil,

        on_activate = function(self, staticdata)
            self._npc_type = npc_def.name
            if not self._npc_def then self._npc_def = npc_def end
            self._timer=0; self._walk_timer=0; self._meet_timer=0; self._stuck_timer=0
            if not npc_dialogs[self._npc_type] then npc_dialogs[self._npc_type] = {} end
            if not npc_tasks[self._npc_type] then npc_tasks[self._npc_type] = {given=false, completed=false} end
            if not npc_mood[self._npc_type] then npc_mood[self._npc_type] = 50 end
            if not npc_relation[self._npc_type] then npc_relation[self._npc_type] = 50 end
            if not npc_memories[self._npc_type] then npc_memories[self._npc_type] = {} end
            if not npc_talk_count[self._npc_type] then npc_talk_count[self._npc_type] = 0 end
            self.object:set_properties({infotext="右键对话: " .. npc_def.display})
            self.object:set_animation({x=1, y=40}, 15, 0)
        end,

        on_rightclick = function(self, clicker)
            if not clicker or not clicker:is_player() then return end
            local pname = clicker:get_player_name()
            if active_dialog[pname] and active_dialog[pname] ~= self._npc_type then
                minetest.chat_send_player(pname, "§e你正在和别人对话，先说 '再见'")
                return
            end
            active_dialog[pname] = self._npc_type
            clicker:get_meta():set_string("ai_town_npc", self._npc_type)
            local nd = self._npc_def
            local mood = npc_mood[self._npc_type] or 50
            local rel = npc_relation[self._npc_type] or 50
            local mood_icon = mood > 75 and "😄" or (mood > 50 and "🙂" or (mood < 25 and "😠" or "😐"))
            local rel_str = rel > 75 and "挚友❤️" or (rel > 50 and "朋友" or (rel > 25 and "熟人" or "陌生人"))
            -- 极简表单: 只显示信息和输入框
            local formspec = "size[8,4]" ..
                "label[0.3,0.3;" .. minetest.colorize(nd.color, nd.display) .. " " .. mood_icon ..
                "  " .. minetest.colorize("#888", "好感:" .. rel .. "(" .. rel_str .. ") 情绪:" .. mood) .. "]" ..
                "textarea[0.3,0.8;7.4,1.5;msg;说点什么... (输入'再见'结束);]" ..
                "button[0.3,2.5;2,1;send;💬发送]" ..
                "button[2.5,2.5;1.5,1;task;📋任务]" ..
                "button[4.2,2.5;1.5,1;gift;🎁送礼]" ..
                "button[5.9,2.5;1.5,1;bye;👋再见]"
            minetest.show_formspec(pname, "ai_town:dialog", formspec)
        end,

        on_punch = function(self, puncher)
            if puncher and puncher:is_player() then
                local pname = puncher:get_player_name()
                npc_mood[self._npc_type] = math.max(0, (npc_mood[self._npc_type] or 50) - 15)
                npc_relation[self._npc_type] = math.max(0, (npc_relation[self._npc_type] or 50) - 10)
                add_memory(self._npc_type, "被玩家打了", 4)
                add_reputation(pname, -5)
                minetest.chat_send_player(pname, "§c" .. self._npc_def.display .. ": 别打我！(好感-10 声望-5)")
            end
        end,

        on_step = function(self, dtime)
            self._timer = (self._timer or 0) + dtime
            if self._timer < 3 then return end  -- 3秒一次，降低性能消耗
            self._timer = 0
            if not self._npc_def then return end

            -- 日程
            local time = minetest.get_timeofday()
            local target
            if time >= 0.25 and time < 0.70 then target = self._npc_def.work_pos
            elseif time >= 0.70 and time < 0.80 then target = self._npc_def.walk_pos
            else target = self._npc_def.home_pos end
            if not target then return end

            local pos = self.object:get_pos()
            if not pos then return end
            local dist = vector.distance(pos, target)

            if dist > 2 then
                local dir = vector.direction(pos, target)
                self.object:set_yaw(math.atan2(dir.z, dir.x))
                -- 避障: 检测前方2格
                local ahead = {x=pos.x+dir.x*1.5, y=pos.y, z=pos.z+dir.z*1.5}
                local node = minetest.get_node_or_nil(ahead)
                local def = node and minetest.registered_nodes[node.name]
                if def and def.walkable then
                    -- 前方有墙，尝试跳跃
                    self.object:set_velocity({x=dir.x*2, y=6, z=dir.z*2})
                else
                    -- 正常行走 + 走路动画
                    self.object:set_velocity({x=dir.x*2.5, y=-4, z=dir.z*2.5})
                    self.object:set_animation({x=1, y=40}, 20, 0)
                end
                -- 卡住检测
                if self._last_pos and vector.distance(pos, self._last_pos) < 0.5 then
                    self._stuck_timer = (self._stuck_timer or 0) + 1
                    if self._stuck_timer > 3 then
                        -- 卡住了，随机方向跳
                        self._stuck_timer = 0
                        local yaw = math.random() * math.pi * 2
                        self.object:set_velocity({x=math.cos(yaw)*3, y=6, z=math.sin(yaw)*3})
                    end
                else
                    self._stuck_timer = 0
                end
                self._last_pos = {x=pos.x, y=pos.y, z=pos.z}
            else
                -- 到达目标，停下 + 站立动画
                self.object:set_velocity({x=0, y=0, z=0})
                self.object:set_animation({x=0, y=0}, 15, 0)
                -- 到达后随机小范围走动
                self._walk_timer = (self._walk_timer or 0) + 1
                if self._walk_timer > 5 then
                    self._walk_timer = 0
                    if math.random() < 0.5 then
                        local yaw = math.random() * math.pi * 2
                        local r = math.random(1, 2)
                        self.object:set_yaw(yaw)
                        self.object:set_velocity({x=math.cos(yaw)*r, y=0, z=math.sin(yaw)*r})
                        self.object:set_animation({x=1, y=40}, 20, 0)
                    end
                end
            end

            -- NPC 相遇自动对话
            self._meet_timer = (self._meet_timer or 0) + 1
            if self._meet_timer > 8 then
                self._meet_timer = 0
                for _, obj in ipairs(minetest.get_objects_inside_radius(pos, 6)) do
                    local ent = obj:get_luaentity()
                    if ent and ent.name and ent.name:match("^ai_town:npc_") and ent.name ~= ("ai_town:npc_" .. self._npc_type) then
                        if math.random() < 0.1 then
                            npc_talk_to_npc(self._npc_type, ent.name:gsub("ai_town:npc_", ""))
                        end
                    end
                end
            end

            -- 情绪恢复
            local m = npc_mood[self._npc_type] or 50
            if m < 50 then npc_mood[self._npc_type] = math.min(50, m + 1) end
        end,
    })
end

-- ============================================================
-- 表单处理 (极简: 发送后直接关表单转聊天框)
-- ============================================================
minetest.register_on_player_receive_fields(function(player, formname, fields)
    local pname = player:get_player_name()

    if formname ~= "ai_town:dialog" then return end

    if fields.bye then
        local npc_type = player:get_meta():get_string("ai_town_npc")
        local nd = nil
        for _, def in ipairs(NPC_TYPES) do if def.name == npc_type then nd = def break end end
        active_dialog[pname] = nil
        if nd then minetest.chat_send_player(pname, "§7[" .. nd.display .. "] 再见！") end
        return
    end

    if fields.task then
        local npc_type = player:get_meta():get_string("ai_town_npc")
        local nd = nil
        for _, def in ipairs(NPC_TYPES) do if def.name == npc_type then nd = def break end end
        if nd then
            local task = npc_tasks[npc_type]
            if not task.given then
                task.desc = nd.quest_desc; task.given = true
                minetest.chat_send_player(pname, "§e[" .. nd.display .. "] 任务: " .. task.desc)
                minetest.chat_send_player(pname, "§7需要: " .. nd.quest_item .. " x" .. nd.quest_count .. " (收集后点🎁送礼)")
            elseif not task.completed then
                minetest.chat_send_player(pname, "§e[" .. nd.display .. "] 任务: " .. (task.desc or "?"))
            else minetest.chat_send_player(pname, "§a[" .. nd.display .. "] 任务已完成！") end
        end return
    end

    if fields.gift then
        local npc_type = player:get_meta():get_string("ai_town_npc")
        local nd = nil
        for _, def in ipairs(NPC_TYPES) do if def.name == npc_type then nd = def break end end
        if not nd then return end
        local inv = player:get_inventory()
        local task = npc_tasks[npc_type]
        -- 档1: 任务物品 (原有逻辑 + 声誉)
        if task and task.given and not task.completed and inv:contains_item("main", nd.quest_item .. " " .. nd.quest_count) then
            inv:remove_item("main", nd.quest_item .. " " .. nd.quest_count)
            task.completed = true
            npc_relation[npc_type] = math.min(100, (npc_relation[npc_type] or 50) + 20)
            npc_mood[npc_type] = math.min(100, (npc_mood[npc_type] or 50) + 30)
            add_memory(npc_type, "玩家帮我完成任务了！", 5)
            add_reputation(pname, 5)
            minetest.chat_send_player(pname, "§a[" .. nd.display .. "] 太好了！好感+20 情绪+30 声望+5")
            minetest.chat_send_player(pname, "§a奖励: 面包x5 发光积木x4 金锭x2")
            inv:add_item("main", "my_first_mod:bread 5")
            inv:add_item("main", "my_first_mod:brick_glow 4")
            inv:add_item("main", "default:gold_ingot 2")
            player_coins[pname] = (player_coins[pname] or 0) + 2
            spawn_particles(player:get_pos(), "sparkle")
        -- 档2: NPC 最爱物品
        elseif nd.liked_item and inv:contains_item("main", nd.liked_item) then
            inv:remove_item("main", nd.liked_item .. " 1")
            npc_relation[npc_type] = math.min(100, (npc_relation[npc_type] or 50) + 8)
            npc_mood[npc_type] = math.min(100, (npc_mood[npc_type] or 50) + 12)
            add_memory(npc_type, "玩家送了我最爱的" .. (nd.liked_desc or "礼物") .. "！", 4)
            add_reputation(pname, 2)
            minetest.chat_send_player(pname, "§a[" .. nd.display .. "] 这正是我最想要的" .. (nd.liked_desc or "") .. "！好感+8 情绪+12 声望+2")
            spawn_particles(player:get_pos(), "hearts")
        -- 档3: 泛用礼物 (面包)
        elseif inv:contains_item("main", "my_first_mod:bread") then
            inv:remove_item("main", "my_first_mod:bread")
            npc_relation[npc_type] = math.min(100, (npc_relation[npc_type] or 50) + 3)
            npc_mood[npc_type] = math.min(100, (npc_mood[npc_type] or 50) + 6)
            add_memory(npc_type, "玩家送了我面包", 3)
            add_reputation(pname, 2)
            minetest.chat_send_player(pname, "§a[" .. nd.display .. "] 谢谢面包！好感+3")
            spawn_particles(player:get_pos(), "hearts")
        else
            local hint = nd.liked_item and (" 最爱:" .. (nd.liked_desc or nd.liked_item)) or ""
            minetest.chat_send_player(pname, "§7[" .. nd.display .. "] 没有合适的礼物。" .. hint .. " (任务:" .. nd.quest_item .. " x" .. nd.quest_count .. ")")
        end return
    end

    if fields.send then
        local msg = (fields.msg or ""):trim()
        if msg == "" then return end
        local npc_type = player:get_meta():get_string("ai_town_npc")
        if not npc_type or npc_type == "" then return end
        local nd = nil
        for _, def in ipairs(NPC_TYPES) do if def.name == npc_type then nd = def break end end
        if not nd then return end

        if msg == "再见" or msg:lower() == "bye" then
            active_dialog[pname] = nil
            minetest.chat_send_player(pname, "§7[" .. nd.display .. "] 再见！") return
        end

        -- 更新状态
        npc_relation[npc_type] = math.min(100, (npc_relation[npc_type] or 50) + 1)
        npc_talk_count[npc_type] = (npc_talk_count[npc_type] or 0) + 1
        add_memory(npc_type, "玩家说: " .. msg, 3)
        if npc_talk_count[npc_type] % 8 == 0 then trigger_reflection(npc_type) end

        -- 关闭表单，转聊天框对话
        minetest.close_formspec(pname, "ai_town:dialog")
        minetest.chat_send_player(pname, "§6[" .. nd.display .. "] 正在思考...")

        local mem_ctx = get_memory_context(npc_type, msg)
        local history = npc_dialogs[npc_type] or {}
        call_ai(pname, nd.system_prompt, history, msg,
            npc_mood[npc_type] or 50, npc_relation[npc_type] or 50, mem_ctx,
            function(reply, err)
                if reply then
                    table.insert(history, {role="user", content=msg})
                    table.insert(history, {role="assistant", content=reply})
                    while #history > AI_CONFIG.max_history * 2 do table.remove(history, 1); table.remove(history, 1) end
                    npc_dialogs[npc_type] = history
                    add_memory(npc_type, "我回复: " .. reply, 2)
                    minetest.chat_send_player(pname, "§f[" .. nd.display .. "] " .. reply)
                else
                    minetest.chat_send_player(pname, "§f[" .. nd.display .. "] " .. fallback_reply(npc_type))
                    if err then minetest.chat_send_player(pname, "§7(API: " .. err .. ")") end
                end
                minetest.chat_send_player(pname, "§7(继续在聊天框输入对话，'再见'结束)")
            end)
        return
    end
end)

-- ============================================================
-- 聊天框直接对话
-- ============================================================
minetest.register_on_chat_message(function(name, message)
    if not active_dialog[name] then return end
    if message:sub(1,1) == "/" then return end
    local npc_type = active_dialog[name]
    local nd = nil
    for _, def in ipairs(NPC_TYPES) do if def.name == npc_type then nd = def break end end
    if not nd then return end

    if message == "再见" or message:lower() == "bye" then
        active_dialog[name] = nil
        minetest.chat_send_player(name, "§7[" .. nd.display .. "] 再见！")
        return true
    end

    npc_relation[npc_type] = math.min(100, (npc_relation[npc_type] or 50) + 1)
    npc_talk_count[npc_type] = (npc_talk_count[npc_type] or 0) + 1
    add_memory(npc_type, "玩家说: " .. message, 3)
    if npc_talk_count[npc_type] % 8 == 0 then trigger_reflection(npc_type) end

    minetest.chat_send_player(name, "§6[" .. nd.display .. "] 正在思考...")
    local history = npc_dialogs[npc_type] or {}
    local mem_ctx = get_memory_context(npc_type, message)
    call_ai(name, nd.system_prompt, history, message,
        npc_mood[npc_type] or 50, npc_relation[npc_type] or 50, mem_ctx,
        function(reply, err)
            if reply then
                table.insert(history, {role="user", content=message})
                table.insert(history, {role="assistant", content=reply})
                while #history > AI_CONFIG.max_history * 2 do table.remove(history, 1); table.remove(history, 1) end
                npc_dialogs[npc_type] = history
                add_memory(npc_type, "我回复: " .. reply, 2)
                minetest.chat_send_player(name, "§f[" .. nd.display .. "] " .. reply)
            else
                minetest.chat_send_player(name, "§f[" .. nd.display .. "] " .. fallback_reply(npc_type))
                if err then minetest.chat_send_player(name, "§7(API: " .. err .. ")") end
            end
        end)
    return true
end)

-- ============================================================
-- 天气 + NPC间对话 + 每日计划 (全局步进)
-- ============================================================
local last_day = -1
minetest.register_globalstep(function(dtime)
    -- 天气变化
    weather_timer = weather_timer + dtime
    if weather_timer > 120 then
        weather_timer = 0
        local r = math.random()
        weather = r < 0.3 and "rain" or (r < 0.5 and "fog" or "clear")
        for _, p in ipairs(minetest.get_connected_players()) do
            local msg = weather == "rain" and "🌧️ 下雨了" or (weather == "fog" and "🌫️ 起雾了" or "☀️ 天晴了")
            minetest.chat_send_player(p:get_player_name(), "§e" .. msg)
        end
        -- 下雨影响NPC情绪
        if weather == "rain" then
            for _, nd in ipairs(NPC_TYPES) do
                npc_mood[nd.name] = math.max(10, (npc_mood[nd.name] or 50) - 5)
                add_memory(nd.name, "下雨了，心情不太好", 2)
            end
        end
    end

    -- NPC间定时对话
    npc_chat_timer = npc_chat_timer + dtime
    if npc_chat_timer > 45 then
        npc_chat_timer = 0
        if town_center then
            local n1 = NPC_TYPES[math.random(#NPC_TYPES)].name
            local n2 = NPC_TYPES[math.random(#NPC_TYPES)].name
            if n1 ~= n2 then npc_talk_to_npc(n1, n2) end
        end
    end

    -- 小镇事件: 3-5 分钟随机触发
    if town_center and #minetest.get_connected_players() > 0 then
        event_timer = event_timer + dtime
        if event_timer > math.random(EVENT_INTERVAL_MIN, EVENT_INTERVAL_MAX) then
            event_timer = 0
            trigger_event()
        end
    end

    -- 每日计划: 新的一天开始时为所有NPC生成计划
    if town_center and #minetest.get_connected_players() > 0 then
        local current_day = math.floor(minetest.get_gametime() / 86400)
        if current_day ~= last_day then
            last_day = current_day
            for _, nd in ipairs(NPC_TYPES) do
                generate_daily_plan(nd.name)
            end
        end
    end
end)

-- ============================================================
-- 小镇生成 (v6: 更大更精美的建筑)
-- ============================================================
minetest.register_chatcommand("town", {
    description = "生成 AI 小镇 v6",
    func = function(name, param)
        local player = minetest.get_player_by_name(name)
        if not player then return false, "玩家不存在" end
        local pos = player:get_pos()
        pos.y = math.floor(pos.y)
        for dy = -3, 3 do
            local node = minetest.get_node_or_nil({x=pos.x, y=pos.y+dy, z=pos.z})
            local def = node and minetest.registered_nodes[node.name]
            if def and def.walkable and node.name ~= "air" then pos.y = pos.y + dy break end
        end
        local dir = player:get_look_dir()
        pos = {x = pos.x + math.floor(dir.x * 15), y = pos.y, z = pos.z + math.floor(dir.z * 15)}
        town_center = pos
        minetest.chat_send_player(name, "§e正在建造 AI 小镇 v6...")

        -- 辅助函数
        local function box(x1,y1,z1,x2,y2,z2,wall)
            for x=x1,x2 do for y=y1,y2 do for z=z1,z2 do
                local p={x=pos.x+x,y=pos.y+y,z=pos.z+z}
                if x==x1 or x==x2 or z==z1 or z==z2 or y==y1 or y==y2 then
                    minetest.set_node(p,{name=wall})
                else minetest.set_node(p,{name="air"}) end
            end end end
        end
        local function roof(x1,z1,x2,z2,y,rtype)
            for x=x1-1,x2+1 do for z=z1-1,z2+1 do
                minetest.set_node({x=pos.x+x,y=pos.y+y,z=pos.z+z},{name=rtype})
            end end
        end
        local function door(cx,cy,cz)
            minetest.set_node({x=pos.x+cx,y=pos.y+cy,z=pos.z+cz},{name="air"})
            minetest.set_node({x=pos.x+cx,y=pos.y+cy+1,z=pos.z+cz},{name="air"})
        end
        local function window(cx,cy,cz)
            minetest.set_node({x=pos.x+cx,y=pos.y+cy,z=pos.z+cz},{name="my_first_mod:brick_white"})
        end
        local function lamp(cx,cz)
            minetest.set_node({x=pos.x+cx,y=pos.y+1,z=pos.z+cz},{name="my_first_mod:brick_gray"})
            minetest.set_node({x=pos.x+cx,y=pos.y+2,z=pos.z+cz},{name="my_first_mod:brick_gray"})
            minetest.set_node({x=pos.x+cx,y=pos.y+3,z=pos.z+cz},{name="my_first_mod:brick_glow"})
        end

        -- 清空
        for x=-25,25 do for y=0,40 do for z=-20,20 do
            minetest.set_node({x=pos.x+x,y=pos.y+y,z=pos.z+z},{name="air"})
        end end end

        -- 道路 (更宽的十字路)
        for z=-18,18 do for x=-2,2 do minetest.set_node({x=pos.x+x,y=pos.y,z=pos.z+z},{name="my_first_mod:brick_gray"}) end end
        for x=-22,22 do for z=-2,2 do minetest.set_node({x=pos.x+x,y=pos.y,z=pos.z+z},{name="my_first_mod:brick_gray"}) end end
        -- 路边草地
        for x=-22,22 do
            minetest.set_node({x=pos.x+x,y=pos.y,z=pos.z+3},{name="default:dirt_with_grass"})
            minetest.set_node({x=pos.x+x,y=pos.y,z=pos.z-3},{name="default:dirt_with_grass"})
        end

        -- 中央广场 (棋盘 + 喷泉)
        for x=-6,6 do for z=-6,6 do
            minetest.set_node({x=pos.x+x,y=pos.y,z=pos.z+z},{name=(x+z)%4<2 and "my_first_mod:brick_white" or "my_first_mod:brick_cyan"})
        end end
        -- 喷泉 (3层)
        for x=-2,2 do for z=-2,2 do
            minetest.set_node({x=pos.x+x,y=pos.y+1,z=pos.z+z},{name="my_first_mod:brick_gray"})
        end end
        for x=-1,1 do for z=-1,1 do
            minetest.set_node({x=pos.x+x,y=pos.y+2,z=pos.z+z},{name="my_first_mod:brick_cyan"})
        end end
        minetest.set_node({x=pos.x,y=pos.y+3,z=pos.z},{name="my_first_mod:brick_glow"})
        minetest.set_node({x=pos.x,y=pos.y+4,z=pos.z},{name="my_first_mod:brick_glow"})

        -- 面包店 (西北, 橙色, 2层带尖顶)
        box(-12,1,-10,-5,5,-5,"my_first_mod:brick_orange"); roof(-12,-10,-5,-5,6,"my_first_mod:brick_yellow")
        door(-9,1,-10); window(-11,3,-10); window(-6,3,-10)
        minetest.set_node({x=pos.x-9,y=pos.y+4,z=pos.z-7},{name="my_first_mod:brick_glow"}) -- 店内灯
        -- 面包店招牌
        minetest.set_node({x=pos.x-9,y=pos.y+1,z=pos.z-11},{name="my_first_mod:brick_orange"})
        minetest.set_node({x=pos.x-9,y=pos.y+2,z=pos.z-11},{name="my_first_mod:brick_glow"})

        -- 图书馆 (东北, 蓝色, 2层带圆顶)
        box(5,1,-10,12,5,-5,"my_first_mod:brick_cyan"); roof(5,-10,12,-5,6,"my_first_mod:brick_blue")
        door(8,1,-10); window(6,3,-10); window(11,3,-10)
        minetest.set_node({x=pos.x+8,y=pos.y+4,z=pos.z-7},{name="my_first_mod:brick_glow"})
        -- 图书馆圆顶
        for x=-2,2 do for z=-2,2 do
            if x*x+z*z<=4 then minetest.set_node({x=pos.x+8+x,y=pos.y+7,z=pos.z-7+z},{name="my_first_mod:brick_blue"}) end
        end end
        minetest.set_node({x=pos.x+8,y=pos.y+8,z=pos.z-7},{name="my_first_mod:brick_glow"})

        -- 市场 (东南, 绿色, 带摊位顶棚)
        box(5,1,5,12,4,10,"my_first_mod:brick_green"); roof(5,5,12,10,5,"my_first_mod:brick_yellow")
        door(8,1,5)
        -- 摊位
        for x=6,11 do minetest.set_node({x=pos.x+x,y=pos.y+1,z=pos.z+8},{name="my_first_mod:brick_gray"}) end
        minetest.set_node({x=pos.x+6,y=pos.y+2,z=pos.z+8},{name="my_first_mod:brick_gray"})
        minetest.set_node({x=pos.x+11,y=pos.y+2,z=pos.z+8},{name="my_first_mod:brick_gray"})
        for x=6,11 do minetest.set_node({x=pos.x+x,y=pos.y+3,z=pos.z+8},{name="my_first_mod:brick_yellow"}) end

        -- 药铺 (西南偏北, 紫色)
        box(-14,1,-3,-10,4,1,"my_first_mod:brick_purple"); roof(-14,-3,-10,1,5,"my_first_mod:brick_pink")
        door(-12,1,-3); minetest.set_node({x=pos.x-12,y=pos.y+3,z=pos.z-1},{name="my_first_mod:brick_glow"})

        -- 住宅 (西南, 粉色, 2栋)
        box(-12,1,4,-7,3,8,"my_first_mod:brick_pink"); roof(-12,4,-7,8,4,"my_first_mod:brick_red"); door(-10,1,4)
        box(-6,1,4,-3,3,8,"my_first_mod:brick_pink"); roof(-6,4,-3,8,4,"my_first_mod:brick_red"); door(-5,1,4)

        -- 城门 (北侧, 更高更壮观)
        for y=1,7 do
            minetest.set_node({x=pos.x-5,y=pos.y+y,z=pos.z-14},{name="my_first_mod:brick_gray"})
            minetest.set_node({x=pos.x+5,y=pos.y+y,z=pos.z-14},{name="my_first_mod:brick_gray"})
        end
        for x=-5,5 do
            minetest.set_node({x=pos.x+x,y=pos.y+7,z=pos.z-14},{name="my_first_mod:brick_gray"})
            minetest.set_node({x=pos.x+x,y=pos.y+8,z=pos.z-14},{name="my_first_mod:brick_glow"})
        end
        -- 城门通道
        for x=-4,4 do for y=1,5 do minetest.set_node({x=pos.x+x,y=pos.y+y,z=pos.z-14},{name="air"}) end end
        -- 城门塔楼
        for y=1,9 do
            minetest.set_node({x=pos.x-6,y=pos.y+y,z=pos.z-14},{name="my_first_mod:brick_gray"})
            minetest.set_node({x=pos.x+6,y=pos.y+y,z=pos.z-14},{name="my_first_mod:brick_gray"})
        end
        minetest.set_node({x=pos.x-6,y=pos.y+10,z=pos.z-14},{name="my_first_mod:brick_glow"})
        minetest.set_node({x=pos.x+6,y=pos.y+10,z=pos.z-14},{name="my_first_mod:brick_glow"})

        -- 城墙
        for x=-22,-7 do for y=1,4 do minetest.set_node({x=pos.x+x,y=pos.y+y,z=pos.z-14},{name="my_first_mod:brick_gray"}) end end
        for x=7,22 do for y=1,4 do minetest.set_node({x=pos.x+x,y=pos.y+y,z=pos.z-14},{name="my_first_mod:brick_gray"}) end end
        for x=-22,22 do for y=1,3 do minetest.set_node({x=pos.x+x,y=pos.y+y,z=pos.z+14},{name="my_first_mod:brick_gray"}) end end
        for z=-14,14 do for y=1,3 do
            minetest.set_node({x=pos.x-22,y=pos.y+y,z=pos.z+z},{name="my_first_mod:brick_gray"})
            minetest.set_node({x=pos.x+22,y=pos.y+y,z=pos.z+z},{name="my_first_mod:brick_gray"})
        end end
        -- 南门
        for x=-2,2 do for y=1,2 do minetest.set_node({x=pos.x+x,y=pos.y+y,z=pos.z+14},{name="air"}) end end

        -- 河流 + 木桥
        for x=-8,8 do
            minetest.set_node({x=pos.x+x,y=pos.y,z=pos.z+16},{name="default:water_source"})
            minetest.set_node({x=pos.x+x,y=pos.y-1,z=pos.z+16},{name="default:water_source"})
            minetest.set_node({x=pos.x+x,y=pos.y,z=pos.z+17},{name="default:water_source"})
            minetest.set_node({x=pos.x+x,y=pos.y-1,z=pos.z+17},{name="default:water_source"})
        end
        for x=-10,10 do
            minetest.set_node({x=pos.x+x,y=pos.y,z=pos.z+15},{name="default:sand"})
            minetest.set_node({x=pos.x+x,y=pos.y,z=pos.z+18},{name="default:dirt_with_grass"})
        end
        for x=-4,4 do
            minetest.set_node({x=pos.x+x,y=pos.y+1,z=pos.z+16},{name="default:wood"})
            minetest.set_node({x=pos.x+x,y=pos.y+1,z=pos.z+17},{name="default:wood"})
        end
        minetest.set_node({x=pos.x-5,y=pos.y+2,z=pos.z+16},{name="default:fence_wood"})
        minetest.set_node({x=pos.x+5,y=pos.y+2,z=pos.z+16},{name="default:fence_wood"})
        minetest.set_node({x=pos.x-5,y=pos.y+2,z=pos.z+17},{name="default:fence_wood"})
        minetest.set_node({x=pos.x+5,y=pos.y+2,z=pos.z+17},{name="default:fence_wood"})

        -- 公园
        for x=14,20 do for z=4,13 do minetest.set_node({x=pos.x+x,y=pos.y,z=pos.z+z},{name="default:dirt_with_grass"}) end end
        for _,tp in ipairs({{15,6},{18,8},{16,11},{19,12}}) do
            minetest.set_node({x=pos.x+tp[1],y=pos.y+1,z=pos.z+tp[2]},{name="default:tree"})
            minetest.set_node({x=pos.x+tp[1],y=pos.y+2,z=pos.z+tp[2]},{name="default:tree"})
            for dy=3,5 do for dx=-1,1 do for dz=-1,1 do
                if dx*dx+dy*dy+dz*dz<=6 then minetest.set_node({x=pos.x+tp[1]+dx,y=pos.y+dy,z=pos.z+tp[2]+dz},{name="default:leaves"}) end
            end end end
        end
        for _,fp in ipairs({{15,9},{17,7},{19,10},{16,12},{18,5}}) do
            minetest.set_node({x=pos.x+fp[1],y=pos.y+1,z=pos.z+fp[2]},{name="flowers:rose"})
        end

        -- 路灯
        lamp(-4,-8); lamp(4,-8); lamp(-4,0); lamp(4,0); lamp(-4,8); lamp(4,8); lamp(-8,0); lamp(8,0)

        -- 生成 NPC (在广场附近, 玩家能直接接触到)
        local spawn_offsets = {
            baker={x=-4,z=-4}, scholar={x=4,z=-4}, merchant={x=4,z=4},
            guard={x=-4,z=4}, healer={x=0,z=-6}, fisher={x=0,z=6},
        }
        for _, nd in ipairs(NPC_TYPES) do
            for _, obj in ipairs(minetest.get_objects_inside_radius(pos, 60)) do
                local ent = obj:get_luaentity()
                if ent and ent.name == "ai_town:npc_" .. nd.name then obj:remove() end
            end
            local off = spawn_offsets[nd.name] or {x=0,z=0}
            local sp = {x=pos.x+off.x, y=pos.y+1, z=pos.z+off.z}
            local obj = minetest.add_entity(sp, "ai_town:npc_" .. nd.name)
            if obj then
                obj:get_luaentity()._npc_def = {
                    name=nd.name, display=nd.display, color=nd.color, system_prompt=nd.system_prompt,
                    work_pos={x=pos.x+nd.work_pos.x,y=pos.y+nd.work_pos.y,z=pos.z+nd.work_pos.z},
                    home_pos={x=pos.x+nd.home_pos.x,y=pos.y+nd.home_pos.y,z=pos.z+nd.home_pos.z},
                    walk_pos={x=pos.x+nd.walk_pos.x,y=pos.y+nd.walk_pos.y,z=pos.z+nd.walk_pos.z},
                }
                add_memory(nd.name, "我是" .. nd.display .. "，住在小镇里", 4)
                -- 生成每日计划 (异步)
                generate_daily_plan(nd.name)
            end
        end

        minetest.chat_send_player(name, "§aAI 小镇 v6 已生成！")
        minetest.chat_send_player(name, "§e6 NPC: 面包师(橙)/学者(蓝)/商人(红)/守卫(绿)/医者(紫)/渔夫(黄)")
        minetest.chat_send_player(name, "§7右键NPC → 输入文字 → 发送 → 之后直接在聊天框对话")
        return true, "OK"
    end,
})

-- ============================================================
-- 命令
-- ============================================================
minetest.register_chatcommand("ai_key", {description="设置API Key", params="<key>",
    func = function(name, param) AI_CONFIG.api_key = (param or ""):trim(); return true, "OK" end})

minetest.register_chatcommand("ai_npc", {description="查看NPC状态",
    func = function(name, param)
        minetest.chat_send_player(name, "§e=== AI 小镇 NPC ===")
        for _, nd in ipairs(NPC_TYPES) do
            local dc = npc_dialogs[nd.name] and #npc_dialogs[nd.name] or 0
            local mood = npc_mood[nd.name] or 50
            local rel = npc_relation[nd.name] or 50
            local mc = npc_memories[nd.name] and #npc_memories[nd.name] or 0
            minetest.chat_send_player(name, string.format("§f%s §7|好感:%d 情绪:%d 对话:%d轮 记忆:%d条",
                nd.display, rel, mood, math.floor(dc/2), mc))
        end
        minetest.chat_send_player(name, "§7天气:" .. weather .. " 金币:" .. (player_coins[name] or 0)) return true
    end})

minetest.register_chatcommand("weather", {description="切换天气", params="clear|rain|fog",
    func = function(name, param)
        local w = (param or ""):trim()
        if w ~= "clear" and w ~= "rain" and w ~= "fog" then return false, "用法: /weather clear|rain|fog" end
        weather = w; weather_timer = 0; return true, "天气: " .. w
    end})

minetest.register_chatcommand("ai_mem", {description="查看NPC记忆", params="<npc_name>",
    func = function(name, param)
        local mems = npc_memories[(param or ""):trim()] or {}
        if #mems == 0 then return true, "无记忆" end
        minetest.chat_send_player(name, "§e记忆 (" .. #mems .. "条):")
        for i = math.max(1,#mems-5), #mems do
            minetest.chat_send_player(name, "§f[" .. i .. "] " .. mems[i].text)
        end
        return true
    end})

minetest.register_chatcommand("event", {description="查看/触发小镇事件", params="[trigger]",
    func = function(name, param)
        if (param or ""):trim() == "trigger" then
            local ev = trigger_event()
            return true, "已触发事件: " .. ev.name
        end
        if current_event then
            return true, "当前事件: " .. current_event.name .. " (手动触发: /event trigger)"
        end
        return true, "当前无事件，等下一次随机触发 (手动: /event trigger)"
    end})

minetest.register_chatcommand("reputation", {description="查看你的镇上声望",
    func = function(name, param)
        local rep = player_reputation[name] or 50
        return true, "你的声望: " .. rep .. "/100 (" .. reputation_str(rep) .. ") — 送礼+2 完成任务+5 打NPC-5"
    end})

minetest.register_on_joinplayer(function(player)
    local name = player:get_player_name()
    if not player_coins[name] then player_coins[name] = 0 end
    if not player_reputation[name] then player_reputation[name] = 50 end
    minetest.after(2, function()
        minetest.chat_send_player(name, "§e=== AI 小镇 v6 ===")
        minetest.chat_send_player(name, "§7/town 生成 | /ai_npc 状态 | /weather 天气 | /ai_mem <npc> 记忆")
        minetest.chat_send_player(name, "§7/event 事件 | /reputation 声望 | 右键NPC对话/送礼")
    end)
end)

print("[ai_town] AI 小镇 v6 加载完成！")
