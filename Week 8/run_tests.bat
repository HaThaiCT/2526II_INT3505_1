@echo off
REM Simple batch script to run Newman tests
echo =======================================
echo   Library API - Newman Test Runner
echo =======================================
echo.

echo Checking Newman installation...
where newman >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Newman is not installed!
    echo Please install: npm install -g newman
    exit /b 1
)
echo Newman is installed!
echo.

echo Running tests...
newman run postman_collection.json --color on

echo.
echo =======================================
echo   Tests Completed!
echo =======================================
pause
