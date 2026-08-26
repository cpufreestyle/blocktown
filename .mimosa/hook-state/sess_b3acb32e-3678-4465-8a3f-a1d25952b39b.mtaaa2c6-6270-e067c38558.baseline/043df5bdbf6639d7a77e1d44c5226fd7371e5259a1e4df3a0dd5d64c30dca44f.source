#!/bin/bash
# Luanti Builder - 一键安装脚本 (macOS/Linux)
set -e

echo "🏗️  Luanti Builder 一键安装"
echo "============================"

# 检查 Python
if ! command -v python3 &>/dev/null; then
    echo "❌ 需要 Python 3，请先安装: https://python.org"
    exit 1
fi
echo "✅ Python3: $(python3 --version)"

# 安装
echo "📦 安装 luanti-builder..."
pip3 install -e . --quiet 2>/dev/null || pip3 install -e . 2>/dev/null || {
    echo "⚠️  pip 安装失败，使用直接运行模式"
}

# 复制 mod 到 Luanti 目录
MT_DIR=""
case "$(uname -s)" in
    Darwin)
        MT_DIR="$HOME/Library/Application Support/minetest"
        ;;
    Linux)
        MT_DIR="${HOME}/.minetest"
        ;;
esac

if [ -n "$MT_DIR" ] && [ -d "$MT_DIR" ]; then
    echo "📁 复制 Mod 到 $MT_DIR/mods/..."
    mkdir -p "$MT_DIR/mods"
    cp -r my_first_mod "$MT_DIR/mods/" 2>/dev/null && echo "  ✅ my_first_mod" || true
    cp -r nl_builder "$MT_DIR/mods/" 2>/dev/null && echo "  ✅ nl_builder" || true

    if [ -d "lego_style" ]; then
        echo "🎨 复制纹理包..."
        mkdir -p "$MT_DIR/texture_packs"
        cp -r lego_style "$MT_DIR/texture_packs/" 2>/dev/null && echo "  ✅ lego_style" || true
    fi

    if [ -f "minetest.conf" ]; then
        echo "⚙️  复制配置..."
        cp minetest.conf "$MT_DIR/minetest.conf" 2>/dev/null && echo "  ✅ minetest.conf" || true
    fi
else
    echo "⚠️  未找到 Luanti/Minetest 目录: $MT_DIR"
    echo "   Mod 需要手动复制"
fi

# 创建 macOS launchd 服务 (可选)
if [ "$(uname -s)" = "Darwin" ]; then
    PLIST="$HOME/Library/LaunchAgents/com.luanti-builder.plist"
    cat > "$PLIST" << EOFPLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.luanti-builder</string>
    <key>ProgramArguments</key>
    <array>
        <string>python3</string>
        <string>$(pwd)/luanti_builder_web.py</string>
    </array>
    <key>RunAtLoad</key>
    <false/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
EOFPLIST
    echo "🚀 macOS 服务已创建: $PLIST"
    echo "   启动: launchctl load $PLIST"
    echo "   停止: launchctl unload $PLIST"
fi

echo ""
echo "✅ 安装完成！"
echo ""
echo "🚀 启动方式:"
echo "   python3 luanti_builder_web.py"
echo "   或: luanti-builder (如果 pip 安装成功)"
echo ""
echo "🌐 浏览器打开: http://localhost:8765"
