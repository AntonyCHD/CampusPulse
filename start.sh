#!/bin/bash
# 快速启动脚本（macOS/Linux）

echo "正在启动群声雷达 - Campus Opinion Radar"

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
if [ ! -f ".venv/installed" ]; then
    echo "安装依赖..."
    pip install -r requirements.txt
    touch .venv/installed
fi

# 检查环境变量
if [ ! -f ".env" ]; then
    echo "复制环境变量模板..."
    cp .env.example .env
    echo "请编辑 .env 文件填入配置"
    exit 1
fi

# 启动后端
echo "启动后端服务..."
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端
echo "启动前端服务..."
streamlit run frontend/streamlit_app.py &
FRONTEND_PID=$!

echo ""
echo "========================================="
echo "群声雷达已启动"
echo "前端: http://localhost:8501"
echo "后端: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
echo "========================================="
echo ""
echo "按 Ctrl+C 停止服务"

# 等待中断信号
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
