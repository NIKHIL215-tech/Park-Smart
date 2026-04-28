@echo off
cd /d "%~dp0"
echo ── ParkSmart Compiler ──────────────────────────────────

:: Check lib/ folder exists
if not exist "lib\" (
    echo [ERROR] lib\ folder not found.
    echo  Create a lib\ folder inside backend\ and place mysql-connector-j-*.jar inside it.
    echo  Download from: https://dev.mysql.com/downloads/connector/j/
    pause & exit /b 1
)

:: Check that at least one jar is present
dir /b "lib\*.jar" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No .jar files found in lib\
    echo  Place mysql-connector-j-*.jar inside backend\lib\
    pause & exit /b 1
)

:: Create output directory
if not exist "out\" mkdir out

:: Compile all Java source files
echo Compiling sources...
javac -cp "lib\*" -d out ^
  src\com\parksmart\model\User.java ^
  src\com\parksmart\model\Slot.java ^
  src\com\parksmart\model\Booking.java ^
  src\com\parksmart\DBConnection.java ^
  src\com\parksmart\dao\UserDAO.java ^
  src\com\parksmart\dao\SlotDAO.java ^
  src\com\parksmart\dao\BookingDAO.java ^
  src\com\parksmart\dao\PaymentDAO.java ^
  src\com\parksmart\handler\ApiHandler.java ^
  src\com\parksmart\Main.java

if errorlevel 1 (
    echo [FAILED] Compilation errors. Fix them and try again.
    pause & exit /b 1
)

echo [OK] Compilation successful!  Run run.bat to start the server.
pause
