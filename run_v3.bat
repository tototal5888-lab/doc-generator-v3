@echo off
echo ========================================
echo AI文檔生成器 V3.0 - 專業多格式版
echo ========================================
echo.

REM 檢查 Python 是否安裝
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [錯誤] 未檢測到 Python，請先安裝 Python 3.10+
    pause
    exit /b 1
)

echo [1/3] 檢查依賴套件...
pip list | findstr "Flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo [安裝] 正在安裝依賴套件...
    pip install -r requirements_v3.txt
) else (
    echo [OK] 依賴套件已就緒
)

echo.
echo [2/3] 創建必要目錄...
if not exist "uploads" mkdir uploads
if not exist "templates_storage" mkdir templates_storage
if not exist "output" mkdir output
if not exist "config" mkdir config
echo [OK] 目錄結構已就緒

echo.
echo [3/3] 啟動應用程式...
echo.
echo ========================================
echo 應用程式啟動中...
echo 訪問地址: http://localhost:5000
echo 按 Ctrl+C 停止服務器
echo ========================================
echo.

python app_v3.py

pause
