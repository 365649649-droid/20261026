@echo off
rem Open this project in VS Code.  Double-click to use.
setlocal
set "CODE=%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"
if not exist "%CODE%" (
    echo.
    echo [ERROR] VS Code not found at:
    echo   %CODE%
    echo.
    echo Install it with:  winget install Microsoft.VisualStudioCode
    echo.
    pause
    exit /b 1
)
echo Opening project in VS Code ...
start "" "%CODE%" "%~dp0." "%~dp0pytest-suite\test_login.py"
exit /b 0
