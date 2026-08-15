"""Luanti Builder - paths 模块。"""
import platform
from pathlib import Path

"""平台路径检测。"""
#!/usr/bin/env python3
"""
Luanti Builder - 自然语言生成 Luanti/Minetest 建筑 (Web版)
跨平台: macOS / Linux / Windows
纯 Python 标准库，无需安装任何依赖

用法: python3 luanti_builder_web.py
浏览器打开 http://localhost:8765
"""


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
