@echo off
setlocal enabledelayedexpansion

echo ==================================================
echo Orchestratex Setup and Test Script
echo ==================================================
echo.

echo Checking system requirements...
:check_python
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.x from: https://www.python.org/downloads/
    echo.
    echo Installation instructions:
    echo 1. Download Python installer from above link
    echo 2. Run installer and check "Add Python to PATH"
    echo 3. Restart your computer after installation
    pause
    exit /b 1
)

python --version | findstr /R "Python 3" >nul
if %errorlevel% neq 0 (
    echo ERROR: Python 2.x detected! Orchestratex requires Python 3.x
    echo Please install Python 3.x from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python version check passed!
echo.

:check_pip
echo Checking pip installation...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip not found!
    echo Please run: python -m ensurepip --upgrade
    pause
    exit /b 1
)

echo pip check passed!
echo.

:check_requirements
echo Checking requirements file...
if not exist "requirements-dev.txt" (
    echo ERROR: requirements-dev.txt not found!
    echo Please ensure you're in the correct directory:
    echo C:\Users\the Arcitect\Orchestratex
    pause
    exit /b 1
)

echo Requirements file found!
echo.

:install_dependencies
echo Installing dependencies...
pip install -r "requirements-dev.txt"
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies!
    echo Common fixes:
    echo 1. Ensure pip is up to date: python -m pip install --upgrade pip
    echo 2. Check internet connection
    echo 3. Run as administrator
    pause
    exit /b 1
)

echo Dependencies installed successfully!
echo.

:run_gui
echo Running GUI Test Runner...
python "gui/test_runner.py"
if %errorlevel% neq 0 (
    echo.
    echo GUI Test Runner failed, trying command line tests...
    echo.
    
    :run_all_tests
    echo Running all tests...
    python -m tests.setup_test_environment
    if %errorlevel% neq 0 (
        echo ERROR: All tests failed!
        echo Check the output above for specific errors
        echo.
        echo Troubleshooting steps:
        echo 1. Check Python version matches requirements
        echo 2. Verify all dependencies are installed
        echo 3. Check for network connectivity issues
        echo 4. Run tests individually:
        echo    python -m tests.setup_test_environment
        echo    python -m tests.additional_test_scenarios --performance
        echo    python -m tests.additional_test_scenarios --security
        echo    python -m tests.additional_test_scenarios --edge
        pause
        exit /b 1
    )
    
    :run_performance
    echo Running performance tests...
    python -m tests.additional_test_scenarios --performance
    if %errorlevel% neq 0 (
        echo ERROR: Performance tests failed!
        echo Check the output above for specific errors
        echo.
        echo Troubleshooting steps:
        echo 1. Check system resources (CPU, RAM)
        echo 2. Close other resource-intensive applications
        echo 3. Run tests again
        pause
        exit /b 1
    )
    
    :run_security
    echo Running security tests...
    python -m tests.additional_test_scenarios --security
    if %errorlevel% neq 0 (
        echo ERROR: Security tests failed!
        echo Check the output above for specific errors
        echo.
        echo Troubleshooting steps:
        echo 1. Verify HSM configuration
        echo 2. Check security policies
        echo 3. Review test logs
        pause
        exit /b 1
    )
    
    :run_edge
    echo Running edge case tests...
    python -m tests.additional_test_scenarios --edge
    if %errorlevel% neq 0 (
        echo ERROR: Edge case tests failed!
        echo Check the output above for specific errors
        echo.
        echo Troubleshooting steps:
        echo 1. Review test scenarios
        echo 2. Check boundary conditions
        echo 3. Review test logs
        pause
        exit /b 1
    )
)

echo.
echo All tests completed successfully!
echo.
echo Test Results Summary:
set /p "=<=== SUCCESS ====>" <nul >test_summary.txt
echo Test Suite Completed Successfully >>test_summary.txt
echo ============================== >>test_summary.txt
echo Date: %date% >>test_summary.txt
echo Time: %time% >>test_summary.txt
echo ============================== >>test_summary.txt

type test_summary.txt
echo.
echo Detailed logs are available in test_summary.txt
echo.
pause
