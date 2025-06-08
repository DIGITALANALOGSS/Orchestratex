@echo off

echo Installing requirements...
pip install -r requirements-dev.txt

echo Running tests...
python -m tests.setup_test_environment

echo Tests completed!
pause
