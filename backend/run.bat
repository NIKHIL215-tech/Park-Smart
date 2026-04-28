@echo off
cd /d "%~dp0"
echo ── ParkSmart Server ────────────────────────────────────
echo  Starting... open http://localhost:8080 in your browser
echo  Press Ctrl+C to stop.
echo ────────────────────────────────────────────────────────
java -cp "out;lib\*" com.parksmart.Main
pause
