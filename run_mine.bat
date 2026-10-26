@echo off
cd /d "%~dp0"
setlocal enabledelayedexpansion

echo ============================================
echo   Replay your own recorded script
echo ============================================
echo.

if not exist "my_recorded.py" (
    echo [ERROR] my_recorded.py not found in this folder.
    echo.
    echo Please do this first:
    echo   1. Double-click record.bat
    echo   2. Copy the generated code from the Inspector
    echo   3. Save it in this folder as my_recorded.py
    echo.
    pause
    exit /b 1
)

echo [0/2] Looking for a working Python...

set "PY="

rem (1) python.org per-user installs (preferred)
for %%V in (314 313 312 311 310) do (
    if exist "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe" (
        set "PY=%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe"
        goto :FOUND
    )
)

rem (2) system-wide installs
for %%V in (314 313 312 311 310) do (
    if exist "C:\Python%%V\python.exe" (
        set "PY=C:\Python%%V\python.exe"
        goto :FOUND
    )
)

rem (3) fallback: env bundled with this folder (playwright preinstalled)
if exist "%USERPROFILE%\.workbuddy\binaries\python\envs\default\Scripts\python.exe" (
    set "PY=%USERPROFILE%\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
    goto :FOUND
)

rem (4) whatever PATH offers, validated right after
set "PY=python"

:FOUND
"%PY%" -c "import sys" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] No working Python found on this PC.
    pause
    exit /b 1
)

echo       Found: %PY%
"%PY%" --version
echo.
echo [1/2] Checking Playwright...
"%PY%" -m pip install --quiet playwright --disable-pip-version-check
if errorlevel 1 (
    echo [INFO] Default source failed, retrying with Tsinghua mirror...
    "%PY%" -m pip install playwright --disable-pip-version-check -i https://pypi.tuna.tsinghua.edu.cn/simple
)

echo [2/2] Running my_recorded.py ...
echo.
"%PY%" my_recorded.py %*

echo.
echo ============================================
echo   Finished.
echo ============================================
pause
endlocal
