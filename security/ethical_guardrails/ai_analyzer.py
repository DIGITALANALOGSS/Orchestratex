import logging
from typing import Dict, Any
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import os

class AIAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        """Initialize AI analyzer for ethical content analysis.
        
        Args:
            config: Configuration dictionary containing:
                - model_name: Name of the model to use
                - device: Device to run on (cpu/gpu)
                - thresholds: Risk thresholds
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Initialize model
        self.device = config.get('device', 'cpu')
        if self.device == 'gpu' and torch.cuda.is_available():
            self.device = 'cuda'
            
        self.model_name = config.get('model_name', 'distilbert-base-uncased-finetuned-sst-2-english')
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.model.to(self.device)
        
        # Load thresholds
        self.thresholds = {
            'risk': config.get('risk_threshold', 0.7),
            'suspicious': config.get('suspicious_threshold', 0.5),
            'malicious': config.get('malicious_threshold', 0.9)
        }
        
    def analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze content using AI/ML.
        
        Args:
            content: Content to analyze
            
        Returns:
            Analysis results
        """
        try:
            # Preprocess content
            processed_content = self._preprocess_content(content)
            
            # Run model
            inputs = self.tokenizer(processed_content, return_tensors="pt", truncation=True, padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # Get probabilities
            probabilities = torch.softmax(outputs.logits, dim=1).cpu().numpy()[0]
            
            # Analyze results
            analysis = {
                'risk_score': float(np.max(probabilities)),
                'categories': self._get_categories(probabilities),
                'confidence': float(np.max(probabilities)),
                'timestamp': datetime.utcnow().isoformat(),
                'requires_review': self._requires_review(probabilities)
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"AI analysis failed: {str(e)}")
            return {
                'error': str(e),
                'risk_score': 0.0,
                'categories': [],
                'confidence': 0.0,
                'requires_review': False
            }
            
    def _preprocess_content(self, content: str) -> str:
        """Preprocess content for analysis.
        
        Args:
            content: Content to preprocess
            
        Returns:
            Processed content
        """
        # Clean content
        content = content.strip()
        content = content.lower()
        
        # Add context
        context = self.config.get('context', '')
        if context:
            content = f"{context} {content}"
            
        return content
        
    def _get_categories(self, probabilities: np.ndarray) -> List[str]:
        """Get risk categories based on probabilities.
        
        Args:
            probabilities: Probability distribution
            
        Returns:
            List of risk categories
        """
        categories = []
        
        if probabilities[0] > self.thresholds['malicious']:
            categories.append('malicious')
        elif probabilities[0] > self.thresholds['risk']:
            categories.append('high_risk')
        elif probabilities[0] > self.thresholds['suspicious']:
            categories.append('suspicious')
            
        return categories
        
    def _requires_review(self, probabilities: np.ndarray) -> bool:
        """Determine if human review is required.
        
        Args:
            probabilities: Probability distribution
            
        Returns:
            True if review is required
        """
        # Check thresholds
        if probabilities[0] > self.thresholds['risk']:
            return True
            
        # Check suspicious patterns
        suspicious_patterns = self.config.get('suspicious_patterns', [])
        if any(pattern in content.lower() for pattern in suspicious_patterns):
            return True
            
        return False
