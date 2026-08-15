# 🏗️ Luanti Builder

自然语言生成 Luanti/Minetest 建筑 — 跨平台 GUI 工具 + 完整游戏 Mod

## ✨ 功能

### 1. Luanti Builder (Web GUI)
- **自然语言输入** — 用中文或英文描述你想要的建筑
- **关键词模式** — 19 种模板建筑即时生成 (离线可用)
- **AI 模式** — 接入 30+ 大模型生成复杂建筑 (比萨斜塔/埃菲尔铁塔等)
- **3D 预览** — 等距视图，拖拽旋转，缩放
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

## 🚀 快速开始

```bash
# 启动 Builder GUI
cd luanti_builder
python3 luanti_builder_web.py
# 浏览器自动打开 http://localhost:8765
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
