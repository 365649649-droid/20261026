@echo off
cd /d "%~dp0"
setlocal enabledelayedexpansion

echo ============================================
echo   Run tests then build the Allure report
echo ============================================
echo.

set "PY="
for %%V in (314 313 312 311 310) do (
    if exist "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe" (
        set "PY=%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe"
        goto :FOUND
    )
)
for %%V in (314 313 312 311 310) do (
    if exist "C:\Python%%V\python.exe" (
        set "PY=C:\Python%%V\python.exe"
        goto :FOUND
    )
)
set "PY=python"

:FOUND
"%PY%" -c "import sys" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No working Python found. Run run.bat once to see how to fix it.
    pause
    exit /b 1
)

set "ALLURE=%LOCALAPPDATA%\allure-cli\allure.cmd"
if not exist "%ALLURE%" (
    echo [ERROR] Allure CLI not found at:
    echo   %ALLURE%
    echo.
    echo Install it with:
    echo   npm install -g allure --prefix "%LOCALAPPDATA%\allure-cli"
    pause
    exit /b 1
)

cd /d "%~dp0pytest-suite"
echo [1/2] Running pytest ...
echo.
"%PY%" -m pytest %*
set "RC=%ERRORLEVEL%"

echo.
echo [2/2] Building report ...
rem Remove the old report first.  Without this, leftover files from the
rem previous run can mix into the new one (or Allure warns that the
rem output directory is not empty).
if exist allure-report rmdir /s /q allure-report
call "%ALLURE%" generate allure-results -o allure-report

echo.
if not "%RC%"=="0" (
    echo [NOTE] Some tests FAILED. Open the report and click the red ones.
) else (
    echo All tests passed.
)
echo.
echo Opening the report in your browser.
echo Close this window when you are done looking.
call "%ALLURE%" open allure-report
endlocal
