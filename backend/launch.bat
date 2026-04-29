@echo off
cd /d "%~dp0"
echo =========================================
echo   ParkSmart  Launch
echo =========================================

where javac >nul 2>&1
if errorlevel 1 (
    echo [ERROR] JDK not found. Install JDK and add it to PATH.
    pause
    exit /b 1
)

if not exist "lib\" (
    echo [ERROR] lib\ folder missing. Place mysql-connector-j-*.jar inside backend\lib\
    pause
    exit /b 1
)
dir /b "lib\*.jar" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No .jar found in lib\. Download MySQL Connector/J and put it in backend\lib\
    pause
    exit /b 1
)

if not exist "out\" mkdir out

echo Step 1/2  Compiling sources...
javac -cp "lib\*" -d out src\com\parksmart\model\User.java src\com\parksmart\model\Slot.java src\com\parksmart\model\Booking.java src\com\parksmart\DBConnection.java src\com\parksmart\dao\UserDAO.java src\com\parksmart\dao\SlotDAO.java src\com\parksmart\dao\BookingDAO.java src\com\parksmart\dao\PaymentDAO.java src\com\parksmart\handler\ApiHandler.java src\com\parksmart\Main.java

if errorlevel 1 (
    echo [FAILED] Compilation errors. Fix them and try again.
    pause
    exit /b 1
)
echo [OK] Compiled.

echo Step 2/2  Starting ParkSmart server...
echo  URL  : http://localhost:8080
echo  Stop : Ctrl+C
echo =========================================
java -cp "out;lib\*" com.parksmart.Main
pause
