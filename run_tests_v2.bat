@echo off
setlocal enabledelayedexpansion

echo Starting Orchestratex Test Suite...

:: Check if in correct directory
if not exist "config\test_config.yaml" (
    echo ERROR: Not in Orchestratex project directory!
    echo Please navigate to the Orchestratex project directory first.
    pause
    exit /b 1
)

:: Install requirements
echo Installing test requirements...
pip install -r requirements-dev.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

:: Run tests
echo Running test environment setup...
python -m tests.setup_test_environment 2>&1 | tee test_output.txt
if %errorlevel% neq 0 (
    echo ERROR: Test setup failed
    echo Check test_output.txt for details
    pause
    exit /b 1
)

:: Run additional test scenarios
echo Running additional test scenarios...
python -m tests.additional_test_scenarios
if %errorlevel% neq 0 (
    echo ERROR: Additional test scenarios failed
    echo Check test_output.txt for details
    pause
    exit /b 1
)

:: Verify results
echo Verifying test results...
python -m tests.verify_results
if %errorlevel% neq 0 (
    echo ERROR: Test verification failed
    echo Check test_output.txt for details
    pause
    exit /b 1
)

:: Show summary
echo Test Suite Completed!
type test_output.txt | findstr /i "ERROR" || echo No errors found!
pause
