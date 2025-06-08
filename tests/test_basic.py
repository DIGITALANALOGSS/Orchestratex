import pytest
import yaml
from pathlib import Path

def test_config_load():
    """Test loading test configuration."""
    config_path = Path('tests') / 'test_config.yaml'
    assert config_path.exists()
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
        assert isinstance(config, dict)
        assert 'test_environment' in config
        assert 'voice' in config
        assert 'quantum' in config
        
    print("\nTest Config:")
    print(f"Environment: {config['test_environment']['environment']}")
    print(f"Log Level: {config['test_environment']['log_level']}")
    print(f"Voice Language: {config['voice']['language']}")
    print(f"Quantum Gates: {', '.join(config['quantum']['gates'])}")

def test_performance_metrics():
    """Test performance configuration."""
    config_path = Path('tests') / 'test_config.yaml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
        
    perf_config = config['performance']
    assert isinstance(perf_config['max_concurrent'], int)
    assert perf_config['max_concurrent'] > 0
    assert isinstance(perf_config['test_duration'], int)
    assert perf_config['test_duration'] > 0
    assert isinstance(perf_config['metrics'], list)
    assert len(perf_config['metrics']) > 0
    
    print("\nPerformance Config:")
    print(f"Max Concurrent: {perf_config['max_concurrent']}")
    print(f"Test Duration: {perf_config['test_duration']} seconds")
    print(f"Metrics: {', '.join(perf_config['metrics'])}")

def test_security_settings():
    """Test security configuration."""
    config_path = Path('tests') / 'test_config.yaml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
        
    security_config = config['security']
    assert security_config['key_size'] >= 2048
    assert security_config['quantum_safe'] is True
    assert security_config['hsm_enabled'] is True
    assert security_config['audit_enabled'] is True
    
    print("\nSecurity Config:")
    print(f"Key Size: {security_config['key_size']} bits")
    print(f"Hash Algorithm: {security_config['hash_algo']}")
    print(f"Encryption: {security_config['encryption']}")
