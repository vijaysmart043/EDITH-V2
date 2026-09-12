@echo off
REM ===========================================================================
REM EDITH — Enhanced Digital Intelligence & Task Handler
REM Launch Script for EDITH Windows Desktop AI Assistant
REM Developed by G.Vijay Raj (vijay smart)
REM ===========================================================================

echo [EDITH] Starting EDITH AI Assistant...
python main.py %*
if %errorlevel% neq 0 (
    echo [EDITH] Process exited with error code %errorlevel%
    pause
)
