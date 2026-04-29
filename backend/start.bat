@echo off
cd /d "%~dp0"
echo =========================================
echo   ParkSmart ^| One-Click Start
echo =========================================

:: Check javac / java on PATH
where javac >nul 2>&1
if errorlevel 1 (
    echo [ERROR] JDK not found. Install JDK 11+ and add it to PATH.
    pause & exit /b 1
)

:: Check lib/ and JAR
if not exist "lib\" (
    echo [ERROR] lib\ folder missing — place mysql-connector-j-*.jar inside backend\lib\
    pause & exit /b 1
)
dir /b "lib\*.jar" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No .jar in lib\ — download MySQL Connector/J and put it in backend\lib\
    pause & exit /b 1
)

:: Compile (always re-compile to pick up any changes)
if not exist "out\" mkdir out
echo Step 1/2  Compiling sources...
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
    echo.
    echo [FAILED] Compilation errors — fix them and try again.
    pause & exit /b 1
)
echo [OK] Compiled.
echo.

:: Start server
echo Step 2/2  Starting ParkSmart server...
echo  URL  : http://localhost:8080
echo  Stop : Ctrl+C
echo =========================================
java -cp "out;lib\*" com.parksmart.Main
pause
