import logging
import yaml
import os
import subprocess
from datetime import datetime
from security.hsm.mock_hsm import MockHSM
from security.threat_model import ThreatModel
from security.quantum_security import QuantumSecurity
from threat_detection_test_environment import ThreatDetectionTestEnvironment

logger = logging.getLogger(__name__)

def setup_test_environment(config_path: str):
    """Setup complete test environment.
    
    Args:
        config_path: Path to test configuration file
    """
    try:
        # Load configuration
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        # Initialize components
        mock_hsm = MockHSM(config['hsm'])
        quantum_security = QuantumSecurity(config['quantum_security'])
        threat_model = ThreatModel(config['model'])
        test_env = ThreatDetectionTestEnvironment(config)
        
        # Initialize HSM
        logger.info("Initializing HSM...")
        mock_hsm.generate_key('kyber', 512)
        mock_hsm.generate_key('rsa', 4096)
        
        # Initialize quantum security
        logger.info("Initializing quantum security...")
        quantum_security.initialize_keys()
        
        # Initialize threat model
        logger.info("Initializing threat model...")
        threat_model._init_runtime()
        
        # Create test data
        logger.info("Creating test data...")
        test_env._load_test_data()
        
        # Verify setup
        logger.info("Verifying setup...")
        verify_setup(mock_hsm, quantum_security, threat_model)
        
        return {
            'hsm': mock_hsm,
            'quantum_security': quantum_security,
            'threat_model': threat_model,
            'test_env': test_env,
            'config': config
        }
        
    except Exception as e:
        logger.error(f"Failed to setup test environment: {str(e)}")
        raise

def verify_setup(mock_hsm, quantum_security, threat_model):
    """Verify all components are working correctly.
    
    Args:
        mock_hsm: MockHSM instance
        quantum_security: QuantumSecurity instance
        threat_model: ThreatModel instance
    """
    try:
        # Verify HSM
        logger.info("Verifying HSM...")
        test_data = b"test data"
        public_key = mock_hsm.keys['kyber'].public_key()
        encrypted = mock_hsm.encrypt(test_data, public_key)
        decrypted = mock_hsm.decrypt(encrypted, 'kyber')
        assert decrypted == test_data
        
        # Verify quantum security
        logger.info("Verifying quantum security...")
        encrypted = quantum_security.encrypt("test")
        decrypted = quantum_security.decrypt(encrypted)
        assert decrypted == "test"
        
        # Verify threat model
        logger.info("Verifying threat model...")
        test_event = {
            'user': 'test_user',
            'action': 'test_action',
            'content': 'test_content',
            'metadata': {
                'timestamp': datetime.utcnow().isoformat()
            }
        }
        prediction = threat_model.predict(test_event)
        assert 'threat_score' in prediction
        
        logger.info("Test environment setup verified successfully")
        
    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
        raise

def run_tests(test_env):
    """Run all tests in the environment.
    
    Args:
        test_env: Test environment instance
    """
    try:
        logger.info("Starting test execution...")
        
        # Run threat detection tests
        logger.info("Running threat detection tests...")
        results = test_env.run_tests()
        
        # Log results
        for category, tests in results.items():
            logger.info(f"\n=== {category.upper()} TESTS ===")
            for test in tests:
                status = "PASSED" if test['status'] == 'success' else "FAILED"
                logger.info(f"Test {status}: {test['case']['action']}")
                if test['status'] != 'success':
                    logger.error(f"Error: {test.get('error', 'Unknown error')}")
                    
        # Check overall success
        all_passed = all(
            test['status'] == 'success'
            for tests in results.values()
            for test in tests
        )
        
        if all_passed:
            logger.info("\nALL TESTS PASSED SUCCESSFULLY!")
        else:
            logger.error("\nTESTS FAILED!")
            raise Exception("Some tests failed")
            
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
        raise

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Setup environment
        test_env = setup_test_environment('config/test_config.yaml')
        
        # Run tests
        run_tests(test_env['test_env'])
        
        logger.info("\n=== TEST ENVIRONMENT SETUP COMPLETE ===")
        logger.info("All components verified and tests passed successfully!")
        
    except Exception as e:
        logger.error(f"Failed to setup test environment: {str(e)}")
