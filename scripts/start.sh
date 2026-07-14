#!/bin/bash

# 启动脚本
# 用于启动后端和前端服务

set -e

echo "=========================================="
echo "知识库聊天机器人 - 启动服务"
echo "=========================================="

# 检查 Ollama 服务
echo "检查 Ollama 服务..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "警告: Ollama 服务未运行"
    echo "请在另一个终端运行: ollama serve"
    echo ""
fi

# 启动后端服务
echo "启动后端服务..."
cd backend

if [ ! -d "venv" ]; then
    echo "错误: 虚拟环境不存在，请先运行 setup.sh"
    exit 1
fi

source venv/bin/activate

# 在后台启动后端
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

echo "后端服务已启动 (PID: $BACKEND_PID)"
echo "日志文件: logs/backend.log"

cd ..

# 等待后端启动
echo "等待后端服务启动..."
sleep 3

# 检查后端是否启动成功
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "后端服务启动成功"
else
    echo "警告: 后端服务可能未完全启动，请检查日志"
fi

# 启动前端服务
echo ""
echo "启动前端服务..."
cd frontend

# 在后台启动前端
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

echo "前端服务已启动 (PID: $FRONTEND_PID)"
echo "日志文件: logs/frontend.log"

cd ..

echo ""
echo "=========================================="
echo "服务启动完成！"
echo "=========================================="
echo ""
echo "访问地址："
echo "  前端界面: http://localhost:5173"
echo "  后端 API: http://localhost:8000"
echo "  API 文档: http://localhost:8000/docs"
echo ""
echo "服务进程："
echo "  后端 PID: $BACKEND_PID"
echo "  前端 PID: $FRONTEND_PID"
echo ""
echo "停止服务："
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "查看日志："
echo "  tail -f logs/backend.log"
echo "  tail -f logs/frontend.log"
echo ""

# 保存 PID 到文件，方便后续停止
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid
