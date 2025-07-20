#!/bin/bash

# AugmentCode-Free M2 macOS 启动脚本
# 自动应用修复并启动最适合的版本

echo "🚀 AugmentCode-Free M2 macOS 启动脚本"
echo "=================================="

# 设置环境变量
export TK_SILENCE_DEPRECATION=1
export PYTHONPATH="$(pwd)"

# 检查系统
echo "🔍 检查系统环境..."
echo "系统: $(uname -s) $(uname -r)"
echo "处理器: $(uname -m)"
echo "Python: $(python3 --version)"

# 检查是否为 Apple Silicon
if [[ $(uname -m) == "arm64" ]]; then
    echo "✅ 检测到 Apple Silicon (M1/M2) 处理器"
    USE_COMPATIBLE=true
else
    echo "ℹ️  Intel 处理器，使用标准版本"
    USE_COMPATIBLE=false
fi

# 检查 tkinter 版本
echo "🔍 检查 tkinter 版本..."
TKINTER_VERSION=$(python3 -c "import tkinter; print(tkinter.TkVersion)" 2>/dev/null)
if [[ $? -eq 0 ]]; then
    echo "tkinter 版本: $TKINTER_VERSION"
    if (( $(echo "$TKINTER_VERSION < 8.6" | bc -l) )); then
        echo "⚠️  tkinter 版本较旧，建议使用兼容版本"
        USE_COMPATIBLE=true
    fi
else
    echo "❌ tkinter 检查失败"
    exit 1
fi

# 选择启动版本
if [[ "$USE_COMPATIBLE" == true ]]; then
    echo ""
    echo "🔧 启动 M2 macOS 兼容版本..."
    echo "此版本专门针对 Apple Silicon + tkinter 8.5 优化"
    echo ""
    
    if [[ -f "gui_m2_compatible.py" ]]; then
        python3 gui_m2_compatible.py
    else
        echo "❌ 兼容版本文件不存在，尝试启动标准版本..."
        python3 main.py
    fi
else
    echo ""
    echo "🚀 启动标准版本..."
    echo ""
    python3 main.py
fi

echo ""
echo "👋 应用已退出"
