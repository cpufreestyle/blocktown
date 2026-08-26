"""Luanti Builder - server 模块。"""
import json
import math
import platform
import re
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
from .paths import get_minetest_dir
from .nlp import parse_input
from .lua_gen import gen_lua
from .llm import BLOCK_TYPE_TO_COLOR, blocks_to_lua, call_llm, call_llm_chat, cmds_to_blocks, parse_llm_json
from .preview import gen_preview_blocks
from .worlds import enable_mod_in_world, install_mod, launch_luanti, list_worlds
from .town import TOWN_NPCS, chat_with_npc
from .webui import HTML_PAGE

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
            elif action == 'ai_chat':
                # 对话式迭代建造: 基于历史与当前建筑增量修改
                api_key = qs.get('api_key', [''])[0]
                base_url = qs.get('base_url', ['https://api.deepseek.com/v1'])[0]
                model = qs.get('model', ['deepseek-chat'])[0]
                do_install = qs.get('install', [''])[0] == '1'
                world_name = qs.get('world', [''])[0]
                if not api_key:
                    self._send_json({"error": "请先设置 API Key"})
                    return
                history = []
                current_cmds = None
                try:
                    history = json.loads(qs.get('history', ['[]'])[0] or '[]')
                    current_cmds = json.loads(qs.get('cmds', [''])[0] or 'null')
                except (ValueError, TypeError):
                    pass
                if not isinstance(history, list):
                    history = []
                try:
                    content = call_llm_chat(api_key, base_url, model, user_input,
                                            history=history, current_cmds=current_cmds)
                    cmds = parse_llm_json(content)
                    if not cmds:
                        self._send_json({"error": "AI 返回格式错误", "raw": content[:500]})
                        return
                    new_cmds = cmds if isinstance(cmds, list) else cmds.get("cmds", [])
                    blocks = cmds_to_blocks(new_cmds)
                    if not blocks:
                        self._send_json({"error": "AI 生成的命令无法转为方块"})
                        return
                    lua, valid_blocks = blocks_to_lua(blocks, user_input)
                    resp = {"lua": lua, "cmds": new_cmds,
                            "blocks": [{"x": b["x"], "y": b["y"], "z": b["z"],
                                        "color": BLOCK_TYPE_TO_COLOR.get(b.get("type", "stone"), "#7f8c8d")}
                                       for b in valid_blocks],
                            "count": len(valid_blocks)}
                    if do_install:
                        mod_path = install_mod(lua)
                        mt_dir = get_minetest_dir()
                        world_dir = str(mt_dir / "worlds" / world_name) if world_name else None
                        world_path = enable_mod_in_world(world_dir)
                        resp.update({"mod_path": mod_path, "world_path": world_path,
                                     "launch": launch_luanti(world_path),
                                     "message": "已安装mod并启动游戏，进入后输入 /build 生成建筑"})
                    self._send_json(resp)
                except Exception as e:
                    self._send_json({"error": str(e)})
            elif action == 'town_npcs':
                # AI 小镇 NPC 名册
                self._send_json({"npcs": TOWN_NPCS})
            elif action == 'town_chat':
                # AI 小镇 NPC 聊天预览 (直连 StepFun)
                npc_name = qs.get('npc', [''])[0]
                message = user_input
                mood = int(qs.get('mood', ['50'])[0] or '50')
                relation = int(qs.get('relation', ['50'])[0] or '50')
                weather = qs.get('weather', ['clear'])[0]
                if not npc_name or not message:
                    self._send_json({"error": "缺少 npc 或 message 参数"})
                    return
                try:
                    history = json.loads(qs.get('history', ['[]'])[0] or '[]')
                except (ValueError, TypeError):
                    history = []
                if not isinstance(history, list):
                    history = []
                try:
                    reply, err = chat_with_npc(npc_name, message, history, mood, relation, weather)
                    if err:
                        self._send_json({"error": err})
                    else:
                        self._send_json({"reply": reply, "npc": npc_name})
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
