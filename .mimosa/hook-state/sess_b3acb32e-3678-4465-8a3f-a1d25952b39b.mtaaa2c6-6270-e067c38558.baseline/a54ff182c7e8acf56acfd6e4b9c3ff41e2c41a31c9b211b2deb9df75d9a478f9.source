# AGENTS.md — Luanti Builder

## 项目概述

自然语言生成 Luanti/Minetest 建筑的 Python 工具：用户输入中文/英文描述（如"建一个红色的城堡"），自动解析关键词、生成 Lua mod 代码，并安装到游戏中。

## 核心模块职责

所有业务逻辑位于 `lb_pkg/` 目录下：

| 模块 | 文件 | 职责 |
|------|------|------|
| 自然语言处理 | `lb_pkg/nlp.py` | 关键词解析器，将用户输入的自然语言提取为结构化参数（建筑类型、颜色、尺寸、材质、特征），支持中英文双语关键词匹配 |
| 大模型接口 | `lb_pkg/llm.py` | LLM API 调用层，通过 OpenAI 兼容接口调用大模型生成复杂建筑的方块命令（cmds），包含命令解析（`parse_llm_json`）、命令转方块（`cmds_to_blocks`）、方块转 Lua 代码（`blocks_to_lua`），以及对话式迭代建造（`call_llm_chat`） |
| Lua 代码生成 | `lb_pkg/lua_gen.py` | 规则式 Lua mod 生成器，根据 NLP 解析结果直接生成建筑 Lua 代码（不依赖大模型），包含 20+ 种建筑类型的模板（城堡、房子、塔、金字塔、桥等） |
| Web 界面 | `lb_pkg/webui.py` | 内嵌 HTML/CSS/JS 的单页 Web 应用，提供建筑描述输入、AI 大模型配置、对话式迭代建造、3D 预览画布、语音输入、生成历史等功能 |
| 3D 预览 | `lb_pkg/preview.py` | 生成预览用的方块列表（含颜色信息），供前端 Canvas 进行等距投影 3D 渲染，支持所有建筑类型 |
| 服务入口 | `lb_pkg/server.py` | HTTP 服务器（`http.server`），路由 `/` 返回 Web UI、`/api` 处理所有 API 请求（parse/generate/install/preview/launch/join/ai_* 等），并自动打开浏览器 |
| 世界管理 | `lb_pkg/worlds.py` | Luanti/Minetest 世界列表查询、mod 安装（写入 `nl_builder/init.lua` + `mod.conf`）、世界配置中启用 mod、跨平台启动游戏（macOS/Linux/Windows） |
| 平台路径检测 | `lb_pkg/paths.py` | 检测当前操作系统（macOS/Linux/Windows），返回对应的 Luanti/Minetest 数据目录路径 |

## 开发约定

- **Python 版本**: ≥ 3.6
- **入口点**: `lb_pkg.server:main`（通过 `setup.py` 注册为 `luanti-builder` 命令行工具）
- **安装方式**: `pip install .` 或 `python setup.py install`（基于 `setup.py`，无额外依赖）
- **启动方式**: 运行 `luanti-builder` 或 `python -m lb_pkg.server`，自动在 `http://localhost:8765` 启动 Web 服务并打开浏览器
- **代码风格**: 纯 Python 标准库，无第三方依赖；模块级 docstring 说明职责
- **跨平台**: macOS / Linux / Windows 三平台路径与启动命令自动适配

## 不要修改的文件

以下目录包含游戏资源文件，非工具代码，不应修改：

- `lego_style/textures/` — 乐高风格纹理贴图（PNG 图片）
- `my_first_mod/` — 示例 mod（包含 `init.lua`、`mod.conf` 及纹理资源），作为游戏内方块定义的参考
- `nl_builder/` — 运行时自动生成的 mod 输出目录
- `lego_style/texture_pack.conf` — 纹理包配置
