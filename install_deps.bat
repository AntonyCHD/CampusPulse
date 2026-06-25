@echo off
chcp 65001 > nul

echo =========================================
echo Installing Dependencies in venv_win
echo =========================================
echo.

cd /d "%~dp0"

REM Activate virtual environment
call .venv\Scripts\activate

echo [1/3] Upgrading pip...
python -m pip install --upgrade pip
echo.

echo [2/3] Installing core dependencies...
pip install -r requirements_latest.txt
echo.

echo [3/3] Installing PyTorch with CUDA 11.8...
echo Detecting your CUDA version...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
echo.

echo =========================================
echo Installation Complete!
echo =========================================
echo.
echo Virtual environment: .venv
echo To activate manually: .venv\Scripts\activate
echo.
pause
