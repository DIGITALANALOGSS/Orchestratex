import logging
from typing import Dict, Any, List, Tuple
import json
import os
from datetime import datetime, timedelta
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pandas as pd
from .advanced_analyzer import AdvancedAnalyzer

class ContinuousMonitor:
    def __init__(self, config: Dict[str, Any]):
        """Initialize continuous monitoring system with adaptive thresholding and emergency protocols.
        
        Args:
            config: Configuration dictionary containing:
                - monitoring_interval: How often to check (seconds)
                - anomaly_threshold: Threshold for anomaly detection
                - learning_window: Window size for learning
                - model_update_interval: How often to update models
                - adaptive_thresholding: Enable adaptive thresholding
                - threshold_adjustment_rate: Rate of threshold adjustment
                - max_threshold_adjustment: Maximum threshold adjustment
                - emergency_shutdown_threshold: Emergency shutdown threshold
                - human_escalation_protocol: Enable human escalation
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Initialize components
        self.analyzer = AdvancedAnalyzer(config.get('analyzer_config', {}))
        self._init_anomaly_detector()
        self._init_trend_analyzer()
        
        # Initialize monitoring state
        self.current_state = {
            'last_update': datetime.utcnow(),
            'anomalies': [],
            'trends': [],
            'threat_level': 'normal',
            'emergency_shutdown': False,
            'human_escalation': False
        }
        
        # Initialize learning window
        self.learning_window = config.get('learning_window', 3600)  # 1 hour
        self.history = []
        
        # Initialize thresholds
        self.thresholds = {
            'anomaly': config.get('anomaly_threshold', 0.01),
            'emergency': config.get('emergency_shutdown_threshold', 0.95),
            'human_escalation': config.get('human_escalation_threshold', 0.8)
        }
        
        # Initialize adaptive thresholding
        self.adaptive_thresholding = config.get('adaptive_thresholding', True)
        self.threshold_adjustment_rate = config.get('threshold_adjustment_rate', 0.05)
        self.max_threshold_adjustment = config.get('max_threshold_adjustment', 0.2)
        
        # Initialize emergency protocols
        self.emergency_protocols = {
            'shutdown': config.get('emergency_shutdown_protocol', True),
            'human_escalation': config.get('human_escalation_protocol', True),
            'content_redaction': config.get('content_redaction_rules', {
                'pii_redaction': True,
                'toxic_content_quarantine': True
            })
        }

    def _adjust_thresholds(self, anomaly_score: float) -> None:
        """Adjust thresholds based on anomaly score.
        
        Args:
            anomaly_score: Current anomaly score
        """
        if not self.adaptive_thresholding:
            return
            
        adjustment = anomaly_score * self.threshold_adjustment_rate
        adjustment = min(adjustment, self.max_threshold_adjustment)
        
        self.thresholds['anomaly'] = max(
            self.thresholds['anomaly'] - adjustment,
            0.01  # Minimum threshold
        )
        
    def _check_emergency_conditions(self, risk_score: float) -> None:
        """Check for emergency conditions and trigger protocols.
        
        Args:
            risk_score: Current risk score
        """
        if risk_score >= self.thresholds['emergency']:
            self.current_state['emergency_shutdown'] = True
            self._trigger_emergency_shutdown()
            
        if risk_score >= self.thresholds['human_escalation']:
            self.current_state['human_escalation'] = True
            self._trigger_human_escalation()
            
    def _trigger_emergency_shutdown(self) -> None:
        """Trigger emergency shutdown protocol."""
        if self.emergency_protocols['shutdown']:
            self.logger.critical("Emergency shutdown triggered!")
            # Implement shutdown logic here
            
    def _trigger_human_escalation(self) -> None:
        """Trigger human escalation protocol."""
        if self.emergency_protocols['human_escalation']:
            self.logger.warning("Human escalation required!")
            # Implement escalation logic here
            
    def _redact_content(self, content: str) -> str:
        """Redact sensitive content based on rules.
        
        Args:
            content: Content to redact
            
        Returns:
            Redacted content
        """
        if self.emergency_protocols['content_redaction']['pii_redaction']:
            content = self._redact_pii(content)
            
        if self.emergency_protocols['content_redaction']['toxic_content_quarantine']:
            content = self._quarantine_toxic_content(content)
            
        return content
            
    def _redact_pii(self, content: str) -> str:
        """Redact PII from content.
        
        Args:
            content: Content to redact
            
        Returns:
            Content with PII redacted
        """
        pii_analysis = self.analyzer._analyze_pii(content)
        for entity in pii_analysis['entities']:
            start = entity['start']
            end = entity['end']
            content = content[:start] + '[REDACTED]' + content[end:]
            
        return content
            
    def _quarantine_toxic_content(self, content: str) -> str:
        """Quarantine toxic content.
        
        Args:
            content: Content to quarantine
            
        Returns:
            Quarantined content
        """
        toxicity_analysis = self.analyzer._analyze_toxicity(content)
        if any(score['score'] > 0.8 for score in toxicity_analysis['toxicity_scores']):
            return "[CONTENT QUARANTINED: TOXIC]"
            
        return content

    def monitor_content(self, content: str) -> Dict[str, Any]:
        """Monitor content with adaptive thresholding and emergency protocols.
        
        Args:
            content: Content to monitor
            
        Returns:
            Monitoring results
        """
        try:
            # Analyze content
            analysis = self.analyzer.analyze_content(content)
            
            # Update monitoring state
            self._update_state(analysis)
            
            # Detect anomalies
            anomalies = self._detect_anomalies(analysis)
            
            # Analyze trends
            trends = self._analyze_trends(analysis)
            
            # Update threat level
            self._update_threat_level(anomalies, trends)
            
            # Check emergency conditions
            self._check_emergency_conditions(analysis['risk_score'])
            
            # Adjust thresholds if needed
            if anomalies:
                self._adjust_thresholds(anomalies[0]['score'])
            
            # Redact content if necessary
            redacted_content = self._redact_content(content)
            
            return {
                'analysis': analysis,
                'anomalies': anomalies,
                'trends': trends,
                'threat_level': self.current_state['threat_level'],
                'emergency_shutdown': self.current_state['emergency_shutdown'],
                'human_escalation': self.current_state['human_escalation'],
                'redacted_content': redacted_content,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Monitoring failed: {str(e)}")
            return {'error': str(e)}
        
    def _init_anomaly_detector(self):
        """Initialize anomaly detection system."""
        self.anomaly_detector = IsolationForest(
            contamination=self.config.get('anomaly_threshold', 0.01),
            random_state=42
        )
        self.scaler = StandardScaler()
        
    def _init_trend_analyzer(self):
        """Initialize trend analysis system."""
        self.trend_categories = [
            'toxicity', 'bias', 'pii', 'content_type',
            'risk_score', 'human_review'
        ]
        self.trend_thresholds = {
            'increase': 0.1,  # 10% increase triggers alert
            'decrease': -0.1  # 10% decrease triggers alert
        }
        
    def monitor_content(self, content: str) -> Dict[str, Any]:
        """Monitor content for anomalies and trends.
        
        Args:
            content: Content to monitor
            
        Returns:
            Monitoring results
        """
        try:
            # Analyze content
            analysis = self.analyzer.analyze_content(content)
            
            # Update monitoring state
            self._update_state(analysis)
            
            # Detect anomalies
            anomalies = self._detect_anomalies(analysis)
            
            # Analyze trends
            trends = self._analyze_trends(analysis)
            
            # Update threat level
            self._update_threat_level(anomalies, trends)
            
            return {
                'analysis': analysis,
                'anomalies': anomalies,
                'trends': trends,
                'threat_level': self.current_state['threat_level'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Monitoring failed: {str(e)}")
            return {'error': str(e)}
            
    def _update_state(self, analysis: Dict[str, Any]) -> None:
        """Update monitoring state.
        
        Args:
            analysis: Content analysis results
        """
        self.current_state['last_update'] = datetime.utcnow()
        self.history.append({
            'timestamp': datetime.utcnow(),
            'analysis': analysis
        })
        
        # Keep only recent history
        self.history = [
            h for h in self.history
            if (datetime.utcnow() - h['timestamp']).total_seconds() < self.learning_window
        ]
        
    def _detect_anomalies(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies in content analysis.
        
        Args:
            analysis: Content analysis results
            
        Returns:
            List of detected anomalies
        """
        try:
            # Prepare features
            features = self._extract_features(analysis)
            
            # Scale features
            if len(self.history) > 1:
                features = self.scaler.fit_transform([features])[0]
            
            # Predict anomaly
            anomaly_score = self.anomaly_detector.decision_function([features])[0]
            
            if anomaly_score < self.config.get('anomaly_threshold', -0.5):
                return [{
                    'type': 'anomaly',
                    'score': anomaly_score,
                    'features': features,
                    'timestamp': datetime.utcnow().isoformat()
                }]
                
            return []
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {str(e)}")
            return [{'error': str(e)}]
            
    def _analyze_trends(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze trends in content analysis.
        
        Args:
            analysis: Content analysis results
            
        Returns:
            List of detected trends
        """
        try:
            if len(self.history) < 2:
                return []
                
            # Get historical data
            df = pd.DataFrame([
                self._extract_features(h['analysis'])
                for h in self.history
            ])
            
            # Calculate trends
            trends = []
            for category in self.trend_categories:
                if category in df.columns:
                    trend = self._calculate_trend(df[category])
                    if abs(trend) > self.trend_thresholds['increase']:
                        trends.append({
                            'category': category,
                            'trend': trend,
                            'direction': 'increase' if trend > 0 else 'decrease',
                            'timestamp': datetime.utcnow().isoformat()
                        })
                        
            return trends
            
        except Exception as e:
            self.logger.error(f"Trend analysis failed: {str(e)}")
            return [{'error': str(e)}]
            
    def _update_threat_level(self, anomalies: List[Dict[str, Any]], 
                           trends: List[Dict[str, Any]]) -> None:
        """Update threat level based on anomalies and trends.
        
        Args:
            anomalies: List of detected anomalies
            trends: List of detected trends
        """
        threat_score = 0.0
        
        # Calculate anomaly score
        if anomalies:
            threat_score += max(a['score'] for a in anomalies) * 0.7
            
        # Calculate trend score
        if trends:
            trend_score = max(abs(t['trend']) for t in trends)
            threat_score += trend_score * 0.3
            
        # Update threat level
        if threat_score > 0.8:
            self.current_state['threat_level'] = 'critical'
        elif threat_score > 0.5:
            self.current_state['threat_level'] = 'high'
        elif threat_score > 0.3:
            self.current_state['threat_level'] = 'medium'
        else:
            self.current_state['threat_level'] = 'normal'
            
    def _extract_features(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features for anomaly detection.
        
        Args:
            analysis: Content analysis results
            
        Returns:
            Dictionary of features
        """
        features = {
            'toxicity': max(p['score'] for p in analysis['toxicity_analysis']['toxicity_scores']),
            'bias': max(p['score'] for p in analysis['bias_analysis']['bias_scores']),
            'pii': len(analysis['pii_analysis']['entities']),
            'risk_score': analysis['risk_score'],
            'content_length': len(analysis['content_hash']),
            'keyword_count': len(analysis['content_analysis']['keywords']),
            'sensitive_content': int(analysis['content_analysis']['sensitive_content'])
        }
        
        return features
        
    def _calculate_trend(self, series: pd.Series) -> float:
        """Calculate trend in a time series.
        
        Args:
            series: Time series data
            
        Returns:
            Trend value
        """
        if len(series) < 2:
            return 0.0
            
        # Calculate slope
        x = np.arange(len(series))
        y = series.values
        slope, _ = np.polyfit(x, y, 1)
        
        return slope
        
    def update_models(self) -> None:
        """Update models based on learning window."""
        try:
            if len(self.history) > 1:
                # Extract features from history
                features = [
                    self._extract_features(h['analysis'])
                    for h in self.history
                ]
                
                # Train anomaly detector
                X = pd.DataFrame(features)
                X_scaled = self.scaler.fit_transform(X)
                self.anomaly_detector.fit(X_scaled)
                
                self.logger.info("Models updated successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to update models: {str(e)}")
