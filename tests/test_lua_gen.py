"""lua_gen 模块测试 — Lua 代码生成输出格式。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lb_pkg.lua_gen import select_block, gen_lua, gen_builder


class TestSelectBlock:
    """select_block 方块选择。"""

    def test_color_red(self):
        assert select_block("red", None) == "my_first_mod:brick_red"

    def test_color_blue(self):
        assert select_block("blue", None) == "my_first_mod:brick_blue"

    def test_material_stone(self):
        assert select_block(None, "stone") == "default:stone"

    def test_material_wood(self):
        assert select_block(None, "wood") == "default:wood"

    def test_color_takes_priority_over_material(self):
        # 当 color 在 lego 表中时，优先返回 lego 方块
        assert select_block("red", "stone") == "my_first_mod:brick_red"

    def test_unknown_returns_default_stone(self):
        assert select_block(None, None) == "default:stone"
        assert select_block("nonexistent", "nonexistent") == "default:stone"

    def test_all_lego_colors(self):
        expected_colors = ["red", "blue", "yellow", "green", "white",
                           "black", "orange", "purple", "pink", "cyan", "gray"]
        for c in expected_colors:
            result = select_block(c, None)
            assert result.startswith("my_first_mod:brick_")


class TestGenLua:
    """gen_lua 输出格式验证。"""

    def _make_params(self, **overrides):
        params = {"type": "house", "color": "red", "size": 1,
                  "material": None, "features": [], "raw": "红色房子"}
        params.update(overrides)
        return params

    def test_returns_string(self):
        lua = gen_lua(self._make_params())
        assert isinstance(lua, str)

    def test_contains_block_definition(self):
        lua = gen_lua(self._make_params())
        assert 'local B = "my_first_mod:brick_red"' in lua

    def test_contains_chatcommand(self):
        lua = gen_lua(self._make_params())
        assert 'minetest.register_chatcommand("build"' in lua

    def test_contains_build_structure(self):
        lua = gen_lua(self._make_params())
        assert "local function build_structure(pos)" in lua

    def test_contains_input_comment(self):
        lua = gen_lua(self._make_params())
        assert "-- 输入: 红色房子" in lua

    def test_default_color_gray_when_no_color_no_material(self):
        lua = gen_lua(self._make_params(color=None, material=None))
        assert 'local B = "my_first_mod:brick_gray"' in lua

    def test_castle_type(self):
        lua = gen_lua(self._make_params(type="castle"))
        assert "fill_shell" in lua
        assert "fill_cylinder" in lua

    def test_pyramid_type(self):
        lua = gen_lua(self._make_params(type="pyramid"))
        assert "for y=0, h do" in lua

    def test_fill_box_helper_present(self):
        lua = gen_lua(self._make_params())
        assert "local function fill_box(" in lua

    def test_fill_shell_helper_present(self):
        lua = gen_lua(self._make_params())
        assert "local function fill_shell(" in lua

    def test_print_statement(self):
        lua = gen_lua(self._make_params())
        assert '[nl_builder] 自然语言建筑 mod 加载完成' in lua


class TestGenBuilder:
    """gen_builder 各建筑类型生成。"""

    def test_house_returns_function(self):
        code = gen_builder("house", "default:stone", 1.0, [])
        assert "local function build_structure(pos)" in code

    def test_castle_returns_function(self):
        code = gen_builder("castle", "default:stone", 1.0, ["towers"])
        assert "local function build_structure(pos)" in code

    def test_tower_returns_function(self):
        code = gen_builder("tower", "default:stone", 1.0, [])
        assert "fill_cylinder" in code

    def test_unknown_type_returns_fallback(self):
        code = gen_builder("unknown_type", "default:stone", 1.0, [])
        assert "local function build_structure(pos)" in code
