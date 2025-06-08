import logging
from typing import Dict, Any, List, Tuple
import numpy as np
from datetime import datetime, timedelta
from collections import deque
import hashlib
from .quantum_security import QuantumSecurity
from .ethical_guardrails.continuous_monitor import ContinuousMonitor
from .threat_model import ThreatModel

logger = logging.getLogger(__name__)

class QuantumThreatMonitor:
    def __init__(self, config: Dict[str, Any]):
        """Initialize quantum-safe threat monitoring system with ONNX-based detection.
        
        Args:
            config: Configuration dictionary containing:
                - threat_detection: Threat detection parameters
                - quantum_security: Quantum-safe security parameters
                - monitoring: Monitoring parameters
                - model: ONNX model configuration
        """
        self.config = config
        
        # Initialize quantum security
        self.qsecurity = QuantumSecurity(config.get('quantum_security', {}))
        
        # Initialize continuous monitoring
        self.monitor = ContinuousMonitor(config.get('monitoring', {}))
        
        # Initialize threat model
        self.threat_model = ThreatModel(config.get('model', {}))
        
        # Initialize threat detection
        self._init_threat_detection()
        
        # Initialize history
        self.anomaly_history = deque(maxlen=1000)
        self.alert_history = deque(maxlen=100)
        self.prediction_history = deque(maxlen=1000)
        
        # Initialize audit logging
        self.audit_log = []
        
    def analyze_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze security event with quantum-safe processing and threat detection.
        
        Args:
            event: Security event to analyze
            
        Returns:
            Analysis results with threat prediction
        """
        try:
            # Encrypt sensitive data
            encrypted_event = self._encrypt_sensitive_data(event)
            
            # Analyze with continuous monitoring
            monitor_results = self.monitor.monitor_content(encrypted_event)
            
            # Get threat prediction
            threat_prediction = self.threat_model.predict(event)
            
            # Update histories
            self.anomaly_history.append(monitor_results['risk_score'])
            self.prediction_history.append(threat_prediction['threat_score'])
            
            # Determine threat response
            response = self._determine_threat_response(
                monitor_results,
                threat_prediction
            )
            
            # Create audit log
            log_entry = self._create_audit_log(
                event,
                monitor_results,
                threat_prediction,
                response
            )
            self.audit_log.append(log_entry)
            
            return {
                'analysis': monitor_results,
                'threat_prediction': threat_prediction,
                'response': response,
                'audit': log_entry,
                'quantum_security': {
                    'key_rotation_age': (datetime.utcnow() - self.qsecurity.last_rotated).total_seconds(),
                    'next_rotation': (self.qsecurity.last_rotated + 
                                    self.qsecurity.key_rotation_interval).isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Threat analysis failed: {str(e)}")
            return {'error': str(e)}
            
    def _determine_threat_response(self, 
                                 monitor_results: Dict[str, Any], 
                                 threat_prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Determine appropriate threat response based on multiple factors.
        
        Args:
            monitor_results: Continuous monitoring results
            threat_prediction: Threat model prediction
            
        Returns:
            Response actions
        """
        # Combine scores
        combined_score = (
            threat_prediction['threat_score'] * 0.7 +
            monitor_results['analysis']['risk_score'] * 0.3
        )
        
        # Check response thresholds
        response = []
        
        if combined_score >= self.response_protocols['isolate_system']:
            response.append('isolate_system')
        
        if combined_score >= self.response_protocols['notify_security']:
            response.append('notify_security_team')
        
        if combined_score >= self.response_protocols['redact_content']:
            response.append('redact_content')
            
        # Check emergency conditions
        if monitor_results['emergency_shutdown'] or threat_prediction['threat_level'] == 'critical':
            response.append('emergency_shutdown')
            
        if monitor_results['human_escalation'] or threat_prediction['threat_level'] == 'high':
            response.append('human_escalation')
            
        return {
            'actions': response,
            'combined_score': combined_score,
            'threat_level': threat_prediction['threat_level'],
            'timestamp': datetime.utcnow().isoformat()
        }
        
    def _init_threat_detection(self) -> None:
        """Initialize threat detection parameters."""
        self.thresholds = self.config.get('threat_detection', {
            'anomaly': 0.85,
            'emergency': 0.95,
            'human_escalation': 0.8,
            'content_redaction': 0.7
        })
        
        self.response_protocols = {
            'isolate_system': self.thresholds['emergency'],
            'notify_security': self.thresholds['human_escalation'],
            'redact_content': self.thresholds['content_redaction']
        }
        
    def analyze_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze security event with quantum-safe processing.
        
        Args:
            event: Security event to analyze
            
        Returns:
            Analysis results with quantum-safe metadata
        """
        try:
            # Encrypt sensitive data
            encrypted_event = self._encrypt_sensitive_data(event)
            
            # Analyze with continuous monitoring
            monitor_results = self.monitor.monitor_content(encrypted_event)
            
            # Update history
            self.anomaly_history.append(monitor_results['risk_score'])
            
            # Determine threat response
            response = self._determine_threat_response(monitor_results)
            
            # Create audit log
            log_entry = self._create_audit_log(event, monitor_results, response)
            self.audit_log.append(log_entry)
            
            return {
                'analysis': monitor_results,
                'response': response,
                'audit': log_entry,
                'quantum_security': {
                    'key_rotation': self.qsecurity.last_rotated.isoformat(),
                    'algorithm': self.qsecurity.config.get('algorithm', 'Kyber-512')
                }
            }
            
        except Exception as e:
            logger.error(f"Threat analysis failed: {str(e)}")
            return {'error': str(e)}
            
    def _encrypt_sensitive_data(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive data in event.
        
        Args:
            event: Event to encrypt
            
        Returns:
            Event with encrypted sensitive data
        """
        sensitive_fields = ['content', 'credentials', 'user_info', 'private_data']
        encrypted_event = event.copy()
        
        for field in sensitive_fields:
            if field in event:
                encrypted_event[field] = self.qsecurity.encrypt(event[field])
                
        return encrypted_event
        
    def _determine_threat_response(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Determine appropriate threat response.
        
        Args:
            results: Monitoring results
            
        Returns:
            Response actions
        """
        risk_score = results['analysis']['risk_score']
        response = []
        
        # Check response thresholds
        if risk_score >= self.response_protocols['isolate_system']:
            response.append('isolate_system')
        
        if risk_score >= self.response_protocols['notify_security']:
            response.append('notify_security_team')
        
        if risk_score >= self.response_protocols['redact_content']:
            response.append('redact_content')
            
        # Check emergency conditions
        if results['emergency_shutdown']:
            response.append('emergency_shutdown')
            
        if results['human_escalation']:
            response.append('human_escalation')
            
        return {
            'actions': response,
            'risk_score': risk_score,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    def _create_audit_log(self, 
                         event: Dict[str, Any], 
                         monitor_results: Dict[str, Any], 
                         response: Dict[str, Any]) -> Dict[str, Any]:
        """Create immutable audit log entry.
        
        Args:
            event: Original event
            monitor_results: Monitoring results
            response: Response actions
            
        Returns:
            Audit log entry
        """
        prev_hash = self.audit_log[-1]['hash'] if self.audit_log else 'genesis'
        
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event': event,
            'monitor_results': monitor_results,
            'response': response,
            'prev_hash': prev_hash,
            'quantum_security': {
                'algorithm': self.qsecurity.config.get('algorithm', 'Kyber-512'),
                'key_rotation': self.qsecurity.last_rotated.isoformat()
            }
        }
        
        # Calculate quantum-resistant hash
        hash_obj = hashlib.shake_256()
        hash_obj.update(json.dumps(log_data, sort_keys=True).encode())
        log_data['hash'] = hash_obj.hexdigest(64)
        
        return log_data
        
    def get_threat_summary(self) -> Dict[str, Any]:
        """Get current threat summary.
        
        Returns:
            Threat summary with statistics
        """
        if not self.anomaly_history:
            return {'status': 'no_data'}
            
        # Calculate statistics
        scores = np.array(list(self.anomaly_history))
        summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'current_score': scores[-1],
            'mean': float(np.mean(scores)),
            'std_dev': float(np.std(scores)),
            'max': float(np.max(scores)),
            'min': float(np.min(scores)),
            'alert_count': len([s for s in scores if s >= self.thresholds['anomaly']]),
            'emergency_count': len([s for s in scores if s >= self.thresholds['emergency']]),
            'quantum_security': {
                'key_rotation_age': (datetime.utcnow() - self.qsecurity.last_rotated).total_seconds(),
                'next_rotation': (self.qsecurity.last_rotated + 
                                self.qsecurity.key_rotation_interval).isoformat()
            }
        }
        
        return summary
