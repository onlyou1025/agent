#!/bin/bash

# 停止服务脚本

echo "停止服务..."

# 停止后端
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
        echo "后端服务已停止 (PID: $BACKEND_PID)"
    else
        echo "后端服务未运行"
    fi
    rm .backend.pid
else
    echo "未找到后端 PID 文件"
fi

# 停止前端
if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
        echo "前端服务已停止 (PID: $FRONTEND_PID)"
    else
        echo "前端服务未运行"
    fi
    rm .frontend.pid
else
    echo "未找到前端 PID 文件"
fi

echo "服务已停止"
