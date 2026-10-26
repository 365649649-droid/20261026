@echo off
cd /d "%~dp0"
setlocal enabledelayedexpansion

echo ============================================
echo   Playwright Day 1 - One Click Runner
echo ============================================
echo.
echo [0/2] Looking for a working Python...

rem ============================================================
rem Find a REAL Python.
rem Note: Windows puts a fake "python.exe" under WindowsApps that
rem only opens Microsoft Store. It fails the probe below, so this
rem script skips it automatically.
rem ============================================================
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
    echo.
    echo Why: this machine only has the Microsoft Store stub,
    echo       which is NOT Python, it just opens the Store.
    echo.
    echo How to fix:
    echo   1. Go to https://www.python.org/downloads/
    echo   2. Download Python 3.11 or newer
    echo   3. Run installer, CHECK the box "Add python.exe to PATH"
    echo   4. Reboot or log off, then double-click run.bat again
    echo.
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
if errorlevel 1 (
    echo [ERROR] Failed to install Playwright. Check your network and retry.
    pause
    exit /b 1
)

echo [2/2] Running the login automation script...
echo.
"%PY%" 01_first_login.py %*

echo.
echo ============================================
echo   Done. Screenshots are saved in this folder.
echo ============================================
pause
endlocal
