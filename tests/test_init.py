import logging
import os
import sys
from pathlib import Path
import pytest
import warnings

logger = logging.getLogger(__name__)

def pytest_configure(config):
    """Configure pytest settings."""
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('tests/test.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set up test environment
    setup_test_environment()
    
    # Register additional markers
    config.addinivalue_line(
        'markers',
        'performance: mark test as performance test'
    )
    config.addinivalue_line(
        'markers',
        'security: mark test as security test'
    )
    config.addinivalue_line(
        'markers',
        'quantum: mark test as quantum test'
    )
    config.addinivalue_line(
        'markers',
        'voice: mark test as voice test'
    )

def setup_test_environment():
    """Set up test environment."""
    # Create necessary directories
    required_dirs = [
        'tests/reports',
        'tests/logs',
        'tests/data'
    ]
    
    for dir_path in required_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Set environment variables
    os.environ['TEST_ENV'] = 'true'
    os.environ['LOG_LEVEL'] = 'debug'
    
    # Ignore specific warnings
    warnings.filterwarnings(
        'ignore',
        category=DeprecationWarning,
        module='.*'
    )
    
    logger.info("Test environment set up successfully")

def pytest_sessionstart(session):
    """Called after the Session object has been created and before performing collection and entering the run test loop."""
    logger.info("Starting test session")
    
    # Verify test configuration
    verify_test_config()

def verify_test_config():
    """Verify test configuration."""
    required_files = [
        'tests/test_config.yaml',
        'tests/test_runner.py',
        'tests/test_init.py',
        'tests/test_scenarios.py',
        'tests/test_automation.py',
        'tests/test_report_generator.py'
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Required test file not found: {file_path}")
    
    logger.info("Test configuration verified")

def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished, right before returning the exit status to the system."""
    logger.info("Test session finished")
    
    # Clean up
    cleanup_test_environment()

def cleanup_test_environment():
    """Clean up test environment."""
    # Clean up temporary files
    temp_files = Path('tests').glob('*.tmp')
    for file in temp_files:
        try:
            file.unlink()
        except Exception as e:
            logger.warning(f"Failed to remove temporary file: {file} - {str(e)}")
    
    logger.info("Test environment cleaned up")
