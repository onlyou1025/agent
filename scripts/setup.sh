#!/bin/bash

# 环境初始化脚本
# 用于首次设置开发环境

set -e

echo "=========================================="
echo "知识库聊天机器人 - 环境初始化"
echo "=========================================="

# 检查 Python 版本
echo "检查 Python 版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 版本: $python_version"

# 检查 Node.js 版本
echo "检查 Node.js 版本..."
node_version=$(node --version 2>&1)
echo "Node.js 版本: $node_version"

# 检查 Ollama
echo "检查 Ollama..."
if command -v ollama &> /dev/null; then
    echo "Ollama 已安装"
    ollama_version=$(ollama --version 2>&1 | head -n 1)
    echo "$ollama_version"
else
    echo "警告: Ollama 未安装"
    echo "请访问 https://ollama.com 安装 Ollama"
    echo "安装后运行: ollama pull llama2"
fi

# 设置后端环境
echo ""
echo "设置后端环境..."
cd backend

if [ ! -d "venv" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv venv
fi

echo "激活虚拟环境..."
source venv/bin/activate

echo "安装 Python 依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 复制环境变量文件
if [ ! -f ".env" ]; then
    echo "创建环境变量配置文件..."
    cp .env.example .env
    echo "已创建 .env 文件，请根据需要修改配置"
fi

cd ..

# 设置前端环境
echo ""
echo "设置前端环境..."
cd frontend

echo "安装前端依赖..."
npm install

cd ..

# 创建数据目录
echo ""
echo "创建数据目录..."
mkdir -p backend/data/uploads
mkdir -p backend/data/vector_db
mkdir -p backend/data/chat_history

echo ""
echo "=========================================="
echo "环境初始化完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 确保 Ollama 服务正在运行: ollama serve"
echo "2. 下载模型: ollama pull llama2"
echo "3. 启动后端: cd backend && source venv/bin/activate && python -m uvicorn app.main:app --reload"
echo "4. 启动前端: cd frontend && npm run dev"
echo ""
echo "或者使用启动脚本: ./scripts/start.sh"
echo ""
