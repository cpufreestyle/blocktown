# 🏗️ Blocktown

Luanti/Minetest AI 工具套件 — 自然语言建筑生成 + AI 小镇 (跨平台)

## ✨ 功能

### 1. Luanti Builder (Web GUI)
- **自然语言输入** — 用中文或英文描述你想要的建筑
- **语音输入** — 🎤 点击说话，浏览器语音识别自动填入并生成
- **关键词模式** — 23 种模板建筑即时生成 (离线可用)
- **AI 模式** — 接入 30+ 大模型生成复杂建筑 (比萨斜塔/埃菲尔铁塔等)
- **AI 审美迭代** — 🔄 AI 审视自己作品的 3D 截图并自动改进，支持 1-3 轮循环（无视觉模型时自动降级纯文本评审）
- **对话式迭代建造** — 💬 多轮对话增量修改："把屋顶改成金色""再加两层塔楼"，上下文本地保存
- **蓝图分享** — 📤 导出 JSON 蓝图 / 🔗 复制分享链接 (打开即重建) / 📦 本地蓝图库
- **建造挑战任务** — 🏗️ NPC 出资委托建筑 (灯塔/喷泉/瞭望塔/凉亭)，游戏内自动验收方块数量，达标全镇声望+15 并轮换下一任务
- **3D 预览** — 等距立方体渲染，拖拽旋转，滚轮缩放
- **一键安装** — 自动生成 Lua mod 并安装到 Luanti
- **一键加入游戏** — 安装 mod → 启用世界 → 启动游戏

### 2. my_first_mod (游戏 Mod)
- 饥饿系统 (HUD + 食物 + 疾跑)
- 自定义生物 (猪 + 暗影怪)
- 乐高风格纹理包 (173 纹理)
- 12 色乐高积木方块 + 发光积木
- 乐高上海城市 (/shanghai)
- 无敌模式 (飞行 + 穿墙 + 满血)
- 命令: /build /fly /tptop /undo /clean_all /heal /shanghai

### 3. nl_builder (AI 建筑 Mod)
- 由 Builder GUI 生成的 AI 建筑 mod
- 支持命令: /build 在前方生成建筑
- 20 种形状命令: box/solid/cyl/cone/sphere/dome/ring/pyramid/arch/stairs/spiral/line/hline/vline/floor/wall/cross/taper/fence/cornice

### 4. lego_style (纹理包)
- 173 个乐高风格纹理
- 覆盖 default 游戏所有主要方块

### 5. AI 小镇 (ai_town mod + Web 端)
- 🎭 **Web 端 NPC 对话** — 直连 AI，无需打开游戏；心情/好感/天气实时影响语气
- 📖 **小镇日报** — AI 为 6 位 NPC 生成第一人称日记（按日缓存）
- 🕸️ **关系图谱** — NPC 两两好感度可视化（线越粗越亲密）
- 🎲 **小镇事件** — 集市/迷路旅人/丰收日/夜间巡逻/故事会随机触发，NPC 联动反应
- ⭐ **玩家声誉** — 全镇共享声望系统：送礼+2 任务+5 打NPC-5，NPC 对话会提及你的名声
- 🎁 **送礼深化** — 每个 NPC 有最爱物品（好感+8），泛用礼物+3，任务物品+20
- 🏗️ **建造挑战** — NPC 出资委托(灯塔/喷泉/瞭望塔/凉亭)，游戏内自动验收，达标全镇声望+15
- 🧠 **记忆流/反思/每日计划** — 参照 Generative Agents 论文

## 🚀 快速开始

### 第一步: 安装 Luanti (Minetest) 游戏

> Luanti（原名 Minetest）是一个开源的 3D 沙盒游戏引擎，本项目基于它运行。

| 系统 | 下载方式 |
|------|---------|
| **macOS** | [下载 .zip](https://github.com/luanti-org/luanti/releases/latest) → 解压 → 拖到 Applications/ |
| **Windows** | [下载 .exe 安装包](https://github.com/luanti-org/luanti/releases/latest) → 运行安装 |
| **Linux** | `sudo apt install luanti` 或 [Flatpak](https://flathub.org/apps/net.minetest.Minetest) |
| **Android** | [Google Play](https://play.google.com/store/apps/details?id=net.minetest.minetest) 或 [F-Droid](https://f-droid.org/packages/net.minetest.minetest/) |

安装后还需要安装 **Minetest Game**（基础游戏内容）：
1. 打开 Luanti → 主菜单 → **Content (内容)**
2. 搜索 **Minetest Game** → 点击安装
3. 回到主菜单 → **Start Game** → 选择 Minetest Game → **New World** 创建新世界

### 第二步: 安装本项目的 Mod 和纹理包

```bash
# 克隆仓库
git clone https://github.com/cpufreestyle/blocktown.git
cd luanti_builder

# 运行一键安装脚本 (自动复制 mod/纹理包到 Luanti 目录)
bash install.sh

# 或手动复制:
# macOS:   cp -r my_first_mod nl_builder ai_town ~/Library/Application\ Support/minetest/mods/
#          cp -r lego_style ~/Library/Application\ Support/minetest/texture_packs/
# Windows: 复制到 %APPDATA%\minetest\mods\ 和 %APPDATA%\minetest\texture_packs\
# Linux:   复制到 ~/.minetest/mods/ 和 ~/.minetest/texture_packs/
```

### 第三步: 在游戏中启用 Mod

1. 打开 Luanti → 选中你的世界 → 点 **Settings (设置)**
2. 在 **Mods (模组)** 标签页中勾选:
   - ✅ `my_first_mod` — 游戏核心 mod
   - ✅ `nl_builder` — AI 建筑生成器
   - ✅ `ai_town` — AI 小镇 NPC 对话系统
3. 在 **Texture Packs (纹理包)** 标签页中选择 `lego_style`
4. 点 **Play** 进入游戏

### 第四步 (可选): 启动 AI 建筑生成器

```bash
# 启动 Builder GUI (浏览器自动打开)
python3 luanti_builder_web.py
# 浏览器访问 http://localhost:8765
```

## 📁 目录结构

```
luanti_builder/
├── luanti_builder_web.py    # 入口 (python3 luanti_builder_web.py)
├── lb_pkg/                   # 主程序包 (Web GUI)
│   ├── paths.py              # 平台路径检测
│   ├── nlp.py                # 关键词解析
│   ├── lua_gen.py            # Lua/mod 生成
│   ├── llm.py                # AI 调用与解析
│   ├── preview.py            # 3D 预览
│   ├── worlds.py             # mod 安装/世界管理/启动
│   ├── webui.py              # 前端页面
│   └── server.py             # HTTP 服务器
├── luanti_builder.py         # tkinter 版本 (备用)
├── minetest.conf             # 游戏配置 (性能优化 + UI缩放)
├── my_first_mod/             # 游戏 Mod (饥饿/生物/乐高/上海)
│   ├── init.lua
│   ├── mod.conf
│   └── textures/             # 57 个纹理
├── nl_builder/               # AI 建筑 Mod (由 GUI 生成)
│   ├── init.lua
│   └── mod.conf
├── lego_style/               # 乐高纹理包
│   ├── texture_pack.conf
│   └── textures/             # 173 个纹理
├── README.md
├── LICENSE
└── .gitignore
```

## 🎮 支持的建筑类型 (关键词模式)

🏰 城堡 | 🏠 房子 | 🗼 塔 | 🔺 金字塔 | 🌉 桥 | 🌷 花园
⛩️ 神殿 | 🗿 雕像 | ⛲ 喷泉 | 💡 灯塔 | 🧱 城墙 | 🌳 树
🚀 飞船 | 🍄 蘑菇 | ❤️ 爱心 | 🔮 球体 | 🌀 螺旋 | 🏘️ 村庄
💨 风车 | 🏯 宝塔 | ⛩️ 凉亭 | 🏙️ 摩天大楼

## 🤖 AI 模式支持的供应商

DeepSeek (推荐) | 智谱 GLM | 通义千问 | Moonshot Kimi | 百川 | MiniMax | 零一万物
阶跃星辰 | 商汤 | 讯飞星火 | 腾讯混元 | 百度文心 | 火山豆包 | 硅基流动
OpenRouter | OpenAI | Claude | Gemini | Groq | Together | Mistral | 等 30+

## 🎮 游戏内命令

| 命令 | 说明 |
|------|------|
| /build | 在前方生成建筑 |
| /undo | 撤销前方建筑 |
| /fly | 切换飞行模式 |
| /tptop | 传送到上方地面 |
| /heal | 恢复满血满饱食度 |
| /shanghai | 生成乐高上海城市 |
| /clean_all | 清除附近乐高方块 |
| /legokit | 获得乐高积木套装 |
| /village | 生成乐高村庄 |
| /summon pig/shadow | 召唤生物 |

## 📐 设计决策

- 建筑从 y=1 开始 (不动地面 y=0)
- /build 填平水中 y=0 的坑为石头
- /build 在玩家前方 15 格生成 (避免罩住玩家)
- 命令大小写不敏感 (修复 macOS Caps Lock bug)
- 无敌模式: fly+fast+noclip 自动开启

## 📄 License

MIT
