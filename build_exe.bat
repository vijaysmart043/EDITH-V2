@echo off
REM ===========================================================================
REM EDITH — Enhanced Digital Intelligence & Task Handler
REM Build Script for EDITH.exe using PyInstaller
REM Developed by G.Vijay Raj (vijay smart)
REM ===========================================================================

echo [EDITH] Initializing Windows Desktop Build Pipeline...

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.10+ is required but not found in PATH.
    pause
    exit /b 1
)

REM Install required dependencies
echo [EDITH] Verifying and installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

REM Execute unit tests prior to packaging
echo [EDITH] Running validation test suite...
python -m unittest discover tests
if %errorlevel% neq 0 (
    echo [ERROR] Unit test suite failed! Halting build for safety.
    pause
    exit /b 1
)

echo [EDITH] All 20 validation tests passed successfully.
echo [EDITH] Compiling native Windows binary: EDITH.exe...

pyinstaller --clean EDITH.spec

if exist "dist\EDITH.exe" (
    echo.
    echo ===========================================================================
    echo [SUCCESS] EDITH.exe successfully created in 'dist\EDITH.exe'!
    echo You can now launch EDITH or place it in shell:startup.
    echo Developed by G.Vijay Raj (vijay smart).
    echo ===========================================================================
) else (
    echo [ERROR] Build completed but dist\EDITH.exe was not generated.
)

pause
