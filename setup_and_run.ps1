# Orchestratex Setup and Test Script

# Function to display colored output
function Write-ColorOutput {
    param(
        [string]$Text,
        [ConsoleColor]$Color = [ConsoleColor]::White
    )
    $originalColor = $Host.UI.RawUI.ForegroundColor
    $Host.UI.RawUI.ForegroundColor = $Color
    Write-Host $Text
    $Host.UI.RawUI.ForegroundColor = $originalColor
}

# Function to run a command with error checking
function Run-Command {
    param(
        [string]$Command,
        [string]$Description
    )
    Write-ColorOutput "`n$Description..." -Color Yellow
    Write-ColorOutput "Running: $Command" -Color Cyan
    
    try {
        $result = & $Command
        if ($LASTEXITCODE -ne 0) {
            Write-ColorOutput "`nERROR: Command failed!" -Color Red
            Write-ColorOutput "Exit code: $LASTEXITCODE" -Color Red
            Write-ColorOutput "Output: $result" -Color Red
            exit 1
        }
        Write-ColorOutput "`nSUCCESS: Command completed successfully!" -Color Green
    }
    catch {
        Write-ColorOutput "`nERROR: Exception occurred!" -Color Red
        Write-ColorOutput "Error: $_" -Color Red
        exit 1
    }
}

# Function to check Python version
function Check-Python {
    Write-ColorOutput "`nChecking Python installation..." -Color Yellow
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3") {
        Write-ColorOutput "Python found: $pythonVersion" -Color Green
        return $true
    }
    else {
        Write-ColorOutput "ERROR: Python 3.x is required!" -Color Red
        Write-ColorOutput "Please install Python 3.x from: https://www.python.org/downloads/" -Color Red
        exit 1
    }
}

# Function to check project structure
function Check-ProjectStructure {
    Write-ColorOutput "`nChecking project structure..." -Color Yellow
    $requiredFiles = @(
        "config/test_config.yaml",
        "tests/setup_test_environment.py",
        "tests/additional_test_scenarios.py",
        "gui/test_runner.py",
        "requirements-dev.txt"
    )
    
    foreach ($file in $requiredFiles) {
        if (-not (Test-Path $file)) {
            Write-ColorOutput "ERROR: Required file not found: $file" -Color Red
            exit 1
        }
    }
    Write-ColorOutput "Project structure verified successfully!" -Color Green
}

# Main script execution
Write-ColorOutput "`nStarting Orchestratex Setup and Test Script" -Color Cyan

# Check Python installation
Check-Python

# Check project structure
Check-ProjectStructure

# Install requirements
Run-Command {
    pip install -r requirements-dev.txt
} "Installing test requirements"

# Run tests using GUI (recommended)
Run-Command {
    python gui/test_runner.py
} "Starting GUI Test Runner"

# If GUI fails, fall back to command line tests
if ($LASTEXITCODE -ne 0) {
    Write-ColorOutput "`nGUI Test Runner failed, falling back to command line tests..." -Color Yellow
    
    # Run all tests
    Run-Command {
        python -m tests.setup_test_environment
    } "Running all tests"
    
    # Run additional test scenarios
    Run-Command {
        python -m tests.additional_test_scenarios --performance
    } "Running performance tests"
    
    Run-Command {
        python -m tests.additional_test_scenarios --security
    } "Running security tests"
    
    Run-Command {
        python -m tests.additional_test_scenarios --edge
    } "Running edge case tests"
}

Write-ColorOutput "`nAll tests completed!" -Color Green
Write-ColorOutput "Check the output above for any errors or warnings." -Color Yellow
Write-ColorOutput "Press any key to exit..." -Color Cyan
$Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
