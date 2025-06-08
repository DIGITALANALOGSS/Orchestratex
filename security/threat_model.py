import logging
import numpy as np
from typing import Dict, Any, List
import onnxruntime as ort
from sklearn.preprocessing import StandardScaler
from .quantum_security import QuantumSecurity

logger = logging.getLogger(__name__)

class ThreatModel:
    def __init__(self, config: Dict[str, Any]):
        """Initialize threat detection model with quantum-safe features.
        
        Args:
            config: Configuration dictionary containing:
                - model_path: Path to ONNX model
                - features: Feature configuration
                - quantum_security: Quantum security parameters
        """
        self.config = config
        
        # Initialize ONNX runtime
        self._init_runtime()
        
        # Initialize feature scaler
        self.scaler = StandardScaler()
        
        # Initialize quantum security
        self.qsecurity = QuantumSecurity(config.get('quantum_security', {}))
        
        # Initialize feature extraction
        self._init_feature_extractors()
        
    def _init_runtime(self) -> None:
        """Initialize ONNX runtime with quantum-safe options."""
        try:
            # Set quantum-safe execution options
            options = ort.SessionOptions()
            options.enable_cpu_mem_arena = True
            options.enable_mem_pattern = True
            options.enable_mem_reuse = True
            
            # Load model with quantum-safe encryption
            model_path = self.config['model_path']
            encrypted_model = self.qsecurity.encrypt_model(model_path)
            
            # Initialize session
            self.session = ort.InferenceSession(
                encrypted_model,
                sess_options=options,
                providers=['CPUExecutionProvider']
            )
            
            logger.info(f"Threat detection model loaded: {model_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ONNX runtime: {str(e)}")
            raise
            
    def _init_feature_extractors(self) -> None:
        """Initialize feature extraction methods."""
        self.feature_extractors = {
            'network': self._extract_network_features,
            'behavior': self._extract_behavior_features,
            'content': self._extract_content_features,
            'context': self._extract_context_features
        }
        
    def _extract_network_features(self, event: Dict[str, Any]) -> Dict[str, float]:
        """Extract network-based features.
        
        Args:
            event: Security event
            
        Returns:
            Network features
        """
        return {
            'ip_entropy': self._calculate_ip_entropy(event.get('source_ip', '')),
            'port_diversity': self._calculate_port_diversity(event.get('ports', [])),
            'connection_rate': event.get('connection_count', 0) / 3600,
            'packet_size': np.mean(event.get('packet_sizes', [0]))
        }
        
    def _extract_behavior_features(self, event: Dict[str, Any]) -> Dict[str, float]:
        """Extract behavior-based features.
        
        Args:
            event: Security event
            
        Returns:
            Behavior features
        """
        return {
            'action_frequency': event.get('action_count', 0) / 3600,
            'deviation_score': self._calculate_behavior_deviation(event),
            'anomaly_score': event.get('anomaly_score', 0.0),
            'pattern_match': self._detect_behavior_patterns(event)
        }
        
    def _extract_content_features(self, event: Dict[str, Any]) -> Dict[str, float]:
        """Extract content-based features.
        
        Args:
            event: Security event
            
        Returns:
            Content features
        """
        return {
            'content_length': len(event.get('content', '')),
            'sensitive_keywords': self._detect_sensitive_keywords(event),
            'data_type_score': self._analyze_data_types(event),
            'encryption_score': self._detect_encryption(event)
        }
        
    def _extract_context_features(self, event: Dict[str, Any]) -> Dict[str, float]:
        """Extract context-based features.
        
        Args:
            event: Security event
            
        Returns:
            Context features
        """
        return {
            'time_of_day': self._calculate_time_of_day(event.get('timestamp', '')),
            'user_role': self._get_user_role_score(event.get('user', '')),
            'system_criticality': self._get_system_criticality(event.get('system', '')),
            'environment_score': self._get_environment_score(event)
        }
        
    def extract_features(self, event: Dict[str, Any]) -> np.ndarray:
        """Extract and process features for threat detection.
        
        Args:
            event: Security event
            
        Returns:
            Processed feature array
        """
        try:
            # Extract all feature types
            features = {}
            for feature_type, extractor in self.feature_extractors.items():
                features.update(extractor(event))
                
            # Convert to array and scale
            feature_array = np.array(list(features.values())).reshape(1, -1)
            return self.scaler.transform(feature_array)
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {str(e)}")
            raise
            
    def predict(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Predict threat level using ONNX model.
        
        Args:
            event: Security event
            
        Returns:
            Prediction results
        """
        try:
            # Extract features
            features = self.extract_features(event)
            
            # Run prediction
            inputs = {self.session.get_inputs()[0].name: features.astype(np.float32)}
            outputs = self.session.run(None, inputs)[0]
            
            # Process results
            threat_score = float(outputs[0][0])
            threat_level = self._map_score_to_level(threat_score)
            
            return {
                'threat_score': threat_score,
                'threat_level': threat_level,
                'features': features.tolist()[0],
                'prediction_time': datetime.utcnow().isoformat(),
                'model_version': self.session.get_modelmeta().version
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise
            
    def _map_score_to_level(self, score: float) -> str:
        """Map threat score to threat level.
        
        Args:
            score: Threat score (0-1)
            
        Returns:
            Threat level
        """
        if score >= 0.9:
            return 'critical'
        elif score >= 0.7:
            return 'high'
        elif score >= 0.5:
            return 'medium'
        else:
            return 'low'
            
    def update_model(self, model_path: str) -> None:
        """Update threat detection model.
        
        Args:
            model_path: Path to new model
            
        Returns:
            None
        """
        try:
            # Encrypt and load new model
            encrypted_model = self.qsecurity.encrypt_model(model_path)
            self.session = ort.InferenceSession(encrypted_model)
            
            logger.info(f"Model updated: {model_path}")
            
        except Exception as e:
            logger.error(f"Failed to update model: {str(e)}")
            raise
            
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information.
        
        Returns:
            Model metadata
        """
        return {
            'version': self.session.get_modelmeta().version,
            'producer': self.session.get_modelmeta().producer_name,
            'last_update': self.session.get_modelmeta().domain,
            'quantum_secure': True
        }
