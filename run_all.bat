@echo off
setlocal enabledelayedexpansion

echo ==================================================
echo Orchestratex Setup and Test Script
echo ==================================================
echo.

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.x from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r "requirements-dev.txt"
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo Running GUI Test Runner...
python "gui/test_runner.py"
if %errorlevel% neq 0 (
    echo.
    echo GUI Test Runner failed, trying command line tests...
    
    echo Running all tests...
    python -m tests.setup_test_environment
    
    echo Running performance tests...
    python -m tests.additional_test_scenarios --performance
    
    echo Running security tests...
    python -m tests.additional_test_scenarios --security
    
    echo Running edge case tests...
    python -m tests.additional_test_scenarios --edge
)

echo.
echo All tests completed!
echo Check the output above for any errors or warnings.
echo.
pause
