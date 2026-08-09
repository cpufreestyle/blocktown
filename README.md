# 🏗️ Luanti Builder

自然语言生成 Luanti/Minetest 建筑 — 跨平台 GUI 工具

## ✨ 功能

- **自然语言输入** — 用中文或英文描述你想要的建筑
- **自动解析** — 识别建筑类型、颜色、尺寸、材质、特征
- **3D 预览** — 等距视图，拖拽旋转，缩放
- **一键安装** — 自动生成 Lua mod 并安装到 Luanti
- **一键加入游戏** — 安装 mod → 启用世界 → 启动游戏
- **跨平台** — macOS / Linux / Windows，纯 Python 标准库，零依赖

## 🎮 支持的建筑类型

| 类型 | 关键词 | 类型 | 关键词 |
|------|--------|------|--------|
| 🏰 城堡 | castle | 🏠 房子 | house |
| 🗼 塔 | tower | 🔺 金字塔 | pyramid |
| 🌉 桥 | bridge | 🌷 花园 | garden |
| ⛩️ 神殿 | temple | 🗿 雕像 | statue |
| ⛲ 喷泉 | fountain | 💡 灯塔 | lighthouse |
| 🧱 城墙 | wall | 🌳 树 | tree |
| 🚀 飞船 | spaceship | 🍄 蘑菇 | mushroom |
| ❤️ 爱心 | heart | 🔮 球体 | sphere |
| 🌀 螺旋塔 | spiral | 🏘️ 村庄 | village |

## 🚀 快速开始

```bash
python3 luanti_builder_web.py
```

浏览器自动打开 http://localhost:8765

## 📋 使用流程

1. 输入描述，如 `建一个红色的城堡，有塔楼`
2. 点击「🚀 生成并安装」
3. 点击「👁️ 预览」查看 3D 效果
4. 点击「🎮 一键加入游戏」启动 Luanti
5. 进游戏后输入 `/build` 生成建筑

## 🎨 颜色支持

红/蓝/黄/绿/白/黑/橙/紫/粉/青/灰

## 📐 尺寸支持

小/中/大/巨大 (small/medium/large/huge)

## 🔧 技术细节

- 纯 Python 标准库，无需 pip install
- 本地 Web 服务器 (port 8765)
- 自动检测 Luanti/Minetest 安装路径
- 自动列出所有可用世界
- 生成 Lua mod 代码，安装到 mods 目录

## 📄 License

MIT
