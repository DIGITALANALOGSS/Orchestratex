from pathlib import Path
import pytest
import docker
import os
import yaml

def pytest_configure(config):
    """Configure pytest with required fixtures."""
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers",
        "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers",
        "security: mark test as security test"
    )

def pytest_addoption(parser):
    """Add command line options for test configuration."""
    parser.addoption(
        "--env",
        action="store",
        default="test",
        help="Environment to run tests against: test, staging, production"
    )
    parser.addoption(
        "--test-data",
        action="store",
        default="tests/data",
        help="Path to test data directory"
    )
    parser.addoption(
        "--coverage",
        action="store_true",
        default=False,
        help="Enable code coverage reporting"
    )

@pytest.fixture(scope="session")
def test_environment(request):
    """Set up test environment."""
    env = request.config.getoption("--env")
    test_data_path = Path(request.config.getoption("--test-data"))
    
    # Create test data directory if it doesn't exist
    test_data_path.mkdir(parents=True, exist_ok=True)
    
    # Load test configuration
    config_path = test_data_path / "config.yaml"
    if not config_path.exists():
        with open(config_path, 'w') as f:
            yaml.dump({
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "name": "test_db",
                    "user": "test_user",
                    "password": "test_password"
                },
                "quantum": {
                    "backend": "aer_simulator",
                    "shots": 1000
                },
                "security": {
                    "level": "test",
                    "encryption_key": "test_key"
                }
            }, f)
    
    # Start test services
    client = docker.from_env()
    containers = []
    
    try:
        # Start PostgreSQL
        postgres_container = client.containers.run(
            "postgres:14",
            environment={
                "POSTGRES_DB": "test_db",
                "POSTGRES_USER": "test_user",
                "POSTGRES_PASSWORD": "test_password"
            },
            ports={"5432/tcp": 5432},
            detach=True
        )
        containers.append(postgres_container)
        
        # Wait for PostgreSQL to be ready
        import time
        time.sleep(5)
        
        yield {
            "env": env,
            "config": config_path,
            "containers": containers
        }
        
    finally:
        # Clean up containers
        for container in containers:
            container.stop()
            container.remove()

@pytest.fixture(scope="function")
def test_data(test_environment):
    """Provide test data path."""
    return Path(test_environment["config"]).parent

@pytest.fixture(scope="function")
def quantum_backend(test_environment):
    """Provide quantum backend for tests."""
    from qiskit import Aer
    backend = Aer.get_backend("aer_simulator")
    return backend

@pytest.fixture(scope="function")
def security_context(test_environment):
    """Provide security context for tests."""
    from cryptography.hazmat.primitives.asymmetric import kyber
    private_key = kyber.generate_private_key()
    return {
        "private_key": private_key,
        "public_key": private_key.public_key()
    }
