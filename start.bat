@echo off
chcp 65001 > nul

echo =========================================
echo Campus Opinion Monitoring System
echo =========================================
echo.

cd /d "%~dp0"
echo Current directory: %CD%
echo.

REM Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment: .venv
    call .venv\Scripts\activate
    echo.
) else (
    echo [WARNING] Virtual environment not found!
    echo Please run install_deps.bat first to create .venv
    pause
    exit /b 1
)

REM Check Python in venv
python --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in virtual environment
    pause
    exit /b 1
)
echo [OK] Python:
python --version
echo [OK] Environment: .venv
echo.

REM Check critical dependencies
python -c "import uvicorn, fastapi" > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Missing dependencies in .venv
    echo Please run: install_deps.bat
    pause
    exit /b 1
)

REM Check Node.js
node --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found
    pause
    exit /b 1
)
echo [OK] Node.js:
node --version
echo.

REM Check frontend dependencies
if not exist "frontend-vue\node_modules" (
    echo [INFO] Installing frontend dependencies...
    cd frontend-vue
    call npm install
    cd ..
    echo.
)

echo [1/2] Starting backend (FastAPI on port 8000)...
start "Backend-Port8000" cmd /k "cd /d "%~dp0" && call .venv\Scripts\activate && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"

echo Waiting for backend to start (10 seconds)...
timeout /t 10 /nobreak > nul

echo [2/2] Starting frontend (Vue on port 5173)...
start "Frontend-Port5173" cmd /k "cd /d "%~dp0frontend-vue" && npm run dev"

echo.
echo =========================================
echo Services starting...
echo.
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000/docs
echo =========================================
echo.
pause
