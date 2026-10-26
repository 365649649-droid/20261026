@echo off
cd /d "%~dp0"
setlocal enabledelayedexpansion

echo ============================================
echo   Playwright Recorder (codegen)
echo ============================================
echo.
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
    echo Install Python 3.11+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo       Found: %PY%
echo.
echo [1/2] Starting the recorder...
echo.
echo Two windows will open:
echo   - Browser: browse normally, log in, click around
echo   - Playwright Inspector: code is generated live on the right
echo.
echo When finished:
echo   1. Look at the Inspector window
echo   2. Copy the generated Python code
echo   3. Save it in this folder as: my_recorded.py
echo   4. Double-click run_mine.bat to replay it
echo.

"%PY%" -m playwright codegen https://www.saucedemo.com/

echo.
echo ============================================
echo   Recorder closed.
echo ============================================
pause
endlocal
