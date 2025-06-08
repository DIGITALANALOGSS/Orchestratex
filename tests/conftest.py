import pytest
import os
import tempfile
from pathlib import Path
import logging
from datetime import datetime
import uuid

# Configure logging for tests
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test.log'),
        logging.StreamHandler()
    ]
)

def pytest_configure(config):
    """Configure pytest settings."""
    # Set up test environment
    os.environ['TESTING'] = 'true'
    os.environ['ENVIRONMENT'] = 'test'
    
    # Configure test database
    test_db_path = tempfile.mkstemp(suffix='.db')[1]
    os.environ['DATABASE_URL'] = f'sqlite:///{test_db_path}'
    
    # Configure test Redis
    os.environ['REDIS_HOST'] = 'localhost'
    os.environ['REDIS_PORT'] = '6379'
    
    # Configure test logging
    logging.getLogger().setLevel(logging.DEBUG)

def pytest_sessionstart(session):
    """Setup before test session starts."""
    # Create test directories
    test_dir = Path('test_data')
    test_dir.mkdir(exist_ok=True)
    
    # Create test assets
    assets_dir = test_dir / 'assets'
    assets_dir.mkdir(exist_ok=True)
    
    # Create test files
    test_files = [
        'main_image.jpg',
        'logo.png',
        'config.json'
    ]
    
    for file in test_files:
        (assets_dir / file).touch()

def pytest_sessionfinish(session, exitstatus):
    """Cleanup after test session ends."""
    # Clean up test data
    test_dir = Path('test_data')
    if test_dir.exists():
        shutil.rmtree(test_dir)

def pytest_addoption(parser):
    """Add command line options for pytest."""
    parser.addoption(
        "--runslow", 
        action="store_true",
        default=False,
        help="run slow tests"
    )

@pytest.fixture(scope="session")
def test_data_dir():
    """Fixture for test data directory."""
    return Path('test_data')

@pytest.fixture(scope="function")
def temp_file():
    """Fixture for temporary file."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        yield f.name
    os.unlink(f.name)

@pytest.fixture(scope="function")
def test_logger():
    """Fixture for test logger."""
    logger = logging.getLogger(str(uuid.uuid4()))
    logger.setLevel(logging.DEBUG)
    return logger

@pytest.fixture(scope="function")
def test_config():
    """Fixture for test configuration."""
    return {
        'project_name': 'Orchestratex',
        'version': '1.0.0',
        'directories': {
            'temp': 'temp',
            'logs': 'logs',
            'assets': 'assets'
        },
        'required_files': [
            'requirements.txt',
            'README.md',
            'DEPLOYMENT.md',
            'config.json'
        ]
    }

@pytest.fixture(scope="function")
def test_environment():
    """Fixture for test environment variables."""
    env_backup = dict(os.environ)
    
    # Set up test environment
    os.environ['TESTING'] = 'true'
    os.environ['ENVIRONMENT'] = 'test'
    
    yield os.environ
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(env_backup)

@pytest.fixture(scope="function")
def test_db():
    """Fixture for test database connection."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(os.getenv('DATABASE_URL'))
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
    engine.dispose()
