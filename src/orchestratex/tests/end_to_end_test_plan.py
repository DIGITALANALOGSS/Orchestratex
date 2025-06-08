import pytest
import logging
from datetime import datetime
from security.quantum_security import QuantumSecurity
from security.threat_monitor import QuantumThreatMonitor
from security.threat_model import ThreatModel
from security.ethical_guardrails.continuous_monitor import ContinuousMonitor

logger = logging.getLogger(__name__)

class TestEndToEnd:
    @pytest.fixture(scope="class")
    def test_config(self):
        """Test configuration fixture."""
        return {
            'quantum_security': {
                'algorithm': 'Kyber-512',
                'key_rotation_interval': 1,  # Daily for testing
                'hsm_enabled': True,
                'hsm_config': {
                    'endpoint': 'http://test-hsm.local',
                    'token': 'test-token',
                    'key_label': 'test_',
                    'timeout': 5
                }
            },
            'model': {
                'model_path': 'test_models/threat_detection.onnx',
                'features': {
                    'network': True,
                    'behavior': True,
                    'content': True,
                    'context': True
                }
            },
            'monitoring': {
                'monitoring_interval': 5,  # 5 seconds for testing
                'anomaly_threshold': 0.01,
                'learning_window': 60,  # 1 minute for testing
                'adaptive_thresholding': True,
                'threshold_adjustment_rate': 0.05,
                'max_threshold_adjustment': 0.2
            },
            'threat_detection': {
                'anomaly': 0.85,
                'emergency': 0.95,
                'human_escalation': 0.8,
                'content_redaction': 0.7
            }
        }
    
    @pytest.fixture(scope="class")
    def test_monitor(self, test_config):
        """Initialize test monitor fixture."""
        return QuantumThreatMonitor(test_config)
    
    def test_quantum_security(self, test_config):
        """Test quantum-safe security operations."""
        qsecurity = QuantumSecurity(test_config['quantum_security'])
        
        # Test key generation
        qsecurity._generate_key_pair()
        assert qsecurity.key_pair is not None
        
        # Test key storage
        if test_config['quantum_security']['hsm_enabled']:
            qsecurity._store_keys_in_hsm()
            
        # Test encryption/decryption
        plaintext = "Test data for encryption"
        encrypted = qsecurity.encrypt(plaintext)
        decrypted = qsecurity.decrypt(encrypted)
        assert decrypted == plaintext
    
    def test_threat_model(self, test_config):
        """Test threat detection model."""
        threat_model = ThreatModel(test_config['model'])
        
        # Test feature extraction
        test_event = {
            'user': 'test_user',
            'action': 'test_action',
            'content': 'Test content',
            'metadata': {
                'source_ip': '127.0.0.1',
                'timestamp': datetime.utcnow().isoformat()
            }
        }
        
        features = threat_model.extract_features(test_event)
        assert isinstance(features, np.ndarray)
        
        # Test prediction
        prediction = threat_model.predict(test_event)
        assert 'threat_score' in prediction
        assert 'threat_level' in prediction
    
    def test_end_to_end(self, test_monitor):
        """Test end-to-end threat monitoring."""
        test_event = {
            'user': 'test_user',
            'action': 'test_action',
            'content': 'Test content',
            'metadata': {
                'source_ip': '127.0.0.1',
                'timestamp': datetime.utcnow().isoformat()
            }
        }
        
        # Test analysis
        results = test_monitor.analyze_event(test_event)
        assert 'analysis' in results
        assert 'threat_prediction' in results
        assert 'response' in results
        
        # Test response protocols
        assert 'actions' in results['response']
        assert 'combined_score' in results['response']
        
        # Test audit logging
        assert 'audit' in results
        assert 'timestamp' in results['audit']
    
    def test_performance(self, test_monitor):
        """Test system performance."""
        import time
        
        test_events = [
            {  # Normal event
                'user': 'user1',
                'action': 'read',
                'content': 'Normal content',
                'metadata': {
                    'source_ip': '192.168.1.100',
                    'timestamp': datetime.utcnow().isoformat()
                }
            },
            {  # Suspicious event
                'user': 'admin',
                'action': 'modify',
                'content': 'Sensitive data access',
                'metadata': {
                    'source_ip': '10.0.0.1',
                    'timestamp': datetime.utcnow().isoformat()
                }
            },
            {  # Malicious event
                'user': 'unknown',
                'action': 'execute',
                'content': 'Malicious code',
                'metadata': {
                    'source_ip': '127.0.0.1',
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
        ]
        
        # Test processing time
        start_time = time.time()
        for event in test_events:
            test_monitor.analyze_event(event)
        end_time = time.time()
        
        processing_time = (end_time - start_time) / len(test_events)
        assert processing_time < 0.1  # Should process each event in <100ms
    
    def test_security(self, test_config):
        """Test security features."""
        qsecurity = QuantumSecurity(test_config['quantum_security'])
        
        # Test key rotation
        initial_keys = qsecurity.key_pair
        qsecurity.auto_rotate_keys()
        assert qsecurity.key_pair != initial_keys
        
        # Test encryption integrity
        plaintext = "Sensitive data"
        encrypted = qsecurity.encrypt(plaintext)
        assert encrypted['hsm_used'] == test_config['quantum_security']['hsm_enabled']
        
        # Test content redaction
        test_event = {
            'content': 'This is sensitive data: PII123'
        }
        results = test_monitor.analyze_event(test_event)
        assert '[REDACTED]' in results['analysis']['redacted_content']
