@echo off
REM 快速启动脚本（Windows）

echo 正在启动群声雷达 - Campus Opinion Radar

REM 检查虚拟环境
if not exist ".venv" (
    echo 创建虚拟环境...
    python -m venv .venv
)

REM 激活虚拟环境
call .venv\Scripts\activate

REM 安装依赖
if not exist ".venv\installed" (
    echo 安装依赖...
    pip install -r requirements.txt
    type nul > .venv\installed
)

REM 检查环境变量
if not exist ".env" (
    echo 复制环境变量模板...
    copy .env.example .env
    echo 请编辑 .env 文件填入配置
    exit /b 1
)

REM 启动后端
echo 启动后端服务...
start "Backend" cmd /k uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

REM 等待后端启动
timeout /t 3 /nobreak > nul

REM 启动前端
echo 启动前端服务...
start "Frontend" cmd /k streamlit run frontend/streamlit_app.py

echo.
echo =========================================
echo 群声雷达已启动
echo 前端: http://localhost:8501
echo 后端: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo =========================================
echo.
echo 关闭窗口停止对应服务

pause
