@echo off
cd /d "%~dp0"
setlocal enabledelayedexpansion

echo ============================================
echo   pytest - UI Test Suite
echo ============================================
echo.

set "PY="
for %%V in (314 313 312 311 310) do (
    if exist "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe" (
        set "PY=%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe"
        goto :FOUND
    )
)
if exist "%USERPROFILE%\.workbuddy\binaries\python\envs\default\Scripts\python.exe" (
    set "PY=%USERPROFILE%\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
    goto :FOUND
)
set "PY=python"

:FOUND
"%PY%" -c "import sys" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No working Python found.
    pause
    exit /b 1
)

echo Using: %PY%
echo.
echo [1/2] Checking dependencies...
"%PY%" -m pip install --quiet pytest playwright --disable-pip-version-check
if errorlevel 1 (
    echo [INFO] Retrying with Tsinghua mirror...
    "%PY%" -m pip install pytest playwright --disable-pip-version-check -i https://pypi.tuna.tsinghua.edu.cn/simple
)

echo [2/2] Running tests...
echo.
"%PY%" -m pytest %*

echo.
echo ============================================
echo   Done. Failed-case screenshots: screenshots\
echo ============================================
pause
endlocal
