@echo off
cd /d "%~dp0"
echo =========================================
echo   ParkSmart  Server
echo =========================================

if not exist "out\com\parksmart\Main.class" (
    echo [ERROR] No compiled classes found. Run compile.bat first.
    pause
    exit /b 1
)

echo  Starting server...
echo  Open http://localhost:8080 in your browser
echo  Press Ctrl+C to stop.
echo =========================================
java -cp "out;lib\*" com.parksmart.Main
pause
