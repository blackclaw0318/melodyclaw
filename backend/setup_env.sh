#!/bin/bash
# MelodyClaw 环境 setup 脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔧 MelodyClaw 环境配置开始..."

# 检查 Python 版本
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Python 版本：$PYTHON_VERSION"

if [[ $(echo "$PYTHON_VERSION < 3.10" | bc -l) -eq 1 ]]; then
    echo "❌ 错误：需要 Python 3.10 或更高版本"
    exit 1
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔌 激活虚拟环境..."
source venv/bin/activate

# 升级 pip
echo "⬆️  升级 pip..."
pip install --upgrade pip

# 安装依赖
echo "📥 安装依赖..."
pip install -r requirements.txt

# 验证安装
echo "✅ 验证安装..."
python -c "import fastapi; import torch; import demucs; print('所有依赖安装成功!')"

echo "🎉 环境配置完成!"
echo ""
echo "使用方法:"
echo "  source venv/bin/activate  # 激活虚拟环境"
echo "  python -m uvicorn app.main:app --reload  # 启动开发服务器"
