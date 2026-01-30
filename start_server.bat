@echo off
echo Starting Document Generator V3...
"C:\Users\TF000054\AppData\Local\Programs\Python\Python311\python.exe" run.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with error code %ERRORLEVEL%.
    pause
)
