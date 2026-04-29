@echo off
cd /d "%~dp0"
echo =========================================
echo   ParkSmart ^| Server
echo =========================================

:: Check compiled classes exist
if not exist "out\com\parksmart\Main.class" (
    echo [ERROR] No compiled classes found in out\
    echo  Run compile.bat first, then run this file.
    pause & exit /b 1
)

echo  Starting server...
echo  Open http://localhost:8080 in your browser
echo  Press Ctrl+C to stop.
echo =========================================
java -cp "out;lib\*" com.parksmart.Main
pause
