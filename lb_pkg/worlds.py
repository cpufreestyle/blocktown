"""Luanti Builder - worlds 模块。"""
import os
import platform
import subprocess
from pathlib import Path
from .paths import get_minetest_dir

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

# --- mod 安装 ---
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
