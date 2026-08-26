"""paths 模块测试 — 平台路径检测。"""
import sys
import platform
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lb_pkg.paths import get_minetest_dir


class TestGetMinetestDir:
    """get_minetest_dir 平台路径检测。"""

    def test_returns_path_object(self):
        result = get_minetest_dir()
        assert isinstance(result, Path)

    @patch("lb_pkg.paths.platform.system", return_value="Darwin")
    def test_macos_returns_library_path(self, mock_system):
        result = get_minetest_dir()
        assert "Library" in str(result)
        assert "Application Support" in str(result)

    @patch("lb_pkg.paths.platform.system", return_value="Linux")
    def test_linux_returns_dot_minetest(self, mock_system):
        result = get_minetest_dir()
        assert ".minetest" in str(result)

    @patch("lb_pkg.paths.platform.system", return_value="Windows")
    def test_windows_returns_appdata(self, mock_system):
        result = get_minetest_dir()
        assert "AppData" in str(result)
        assert "Roaming" in str(result)

    @patch("lb_pkg.paths.platform.system", return_value="Unknown")
    def test_unknown_system_fallback(self, mock_system):
        result = get_minetest_dir()
        # 未知系统应回退到 ~/.minetest
        assert str(result).endswith(".minetest")

    @patch("lb_pkg.paths.platform.system", return_value="Darwin")
    def test_macos_path_contains_minetest_or_luanti(self, mock_system):
        result = get_minetest_dir()
        path_str = str(result).lower()
        assert "minetest" in path_str or "luanti" in path_str

    def test_current_platform_returns_valid_path(self):
        # 在当前真实平台上运行，确保返回合理路径
        result = get_minetest_dir()
        system = platform.system()
        if system == "Darwin":
            assert "Application Support" in str(result)
        elif system == "Linux":
            assert ".minetest" in str(result) or ".local" in str(result)
        elif system == "Windows":
            assert "AppData" in str(result)
