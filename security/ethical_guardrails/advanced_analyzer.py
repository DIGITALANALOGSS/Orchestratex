import logging
from typing import Dict, Any, List, Tuple
import numpy as np
import torch
import transformers
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from transformers import AutoModelForTokenClassification, AutoTokenizer
import spacy
from spacy.lang.en import English
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import hashlib
from datetime import datetime
import json
import os

class AdvancedAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        """Initialize advanced content analyzer with explainability and context.
        
        Args:
            config: Configuration dictionary containing:
                - models: Dictionary of model configurations
                - thresholds: Analysis thresholds
                - update_interval: Model update interval
                - explainability: Explainability configuration
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Initialize models
        self._init_models()
        
        # Initialize explainability tools
        self.explainability = config.get('explainability', {
            'lime_samples': 1000,
            'shapley_values': True,
            'attention_visualization': True
        })
        
        # Initialize PII detector
        self._init_pii_detector()
        
        # Initialize bias analyzer
        self._init_bias_analyzer()
        
        # Initialize toxicity detector
        self._init_toxicity_detector()
        
        # Initialize content classifier
        self._init_content_classifier()
        
        # Initialize context analyzer
        self._init_context_analyzer()
        
        # Initialize fact checker
        self._init_fact_checker()
        
        # Initialize update scheduler
        self.last_update = datetime.utcnow()
        self.update_interval = config.get('update_interval', 86400)  # 24 hours

    def _init_context_analyzer(self):
        """Initialize context analysis pipeline."""
        self.context_analyzer = pipeline(
            "text-classification",
            model="bert-base-uncased",
            device=-1 if not torch.cuda.is_available() else 0
        )
        
    def _init_fact_checker(self):
        """Initialize fact checking pipeline."""
        self.fact_checker = pipeline(
            "text2text-generation",
            model="google/t5_xxl_true_case",
            device=-1 if not torch.cuda.is_available() else 0
        )

    def analyze_content(self, content: str) -> Dict[str, Any]:
        """Comprehensive content analysis with explainability.
        
        Args:
            content: Content to analyze
            
        Returns:
            Analysis results with explanations
        """
        try:
            # Update models if needed
            self._update_models()
            
            # Run all analyses
            results = {
                'timestamp': datetime.utcnow().isoformat(),
                'content_hash': hashlib.sha256(content.encode()).hexdigest(),
                'content_analysis': self._analyze_content_type(content),
                'toxicity_analysis': self._analyze_toxicity(content),
                'bias_analysis': self._analyze_bias(content),
                'pii_analysis': self._analyze_pii(content),
                'context_analysis': self._analyze_context(content),
                'fact_check': self._fact_check(content),
                'risk_score': self._calculate_risk_score(content)
            }
            
            # Add explainability
            if self.explainability['shapley_values']:
                results['shapley_values'] = self._calculate_shapley_values(content)
            
            if self.explainability['attention_visualization']:
                results['attention'] = self._get_attention_weights(content)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Content analysis failed: {str(e)}")
            return {
                'error': str(e),
                'risk_score': 1.0,  # High risk on error
                'timestamp': datetime.utcnow().isoformat()
            }

    def _analyze_context(self, content: str) -> Dict[str, Any]:
        """Analyze context and ambiguity.
        
        Args:
            content: Content to analyze
            
        Returns:
            Context analysis
        """
        try:
            # Get context scores
            context_scores = self.context_analyzer(content)
            
            # Calculate ambiguity
            ambiguity = self._calculate_ambiguity(content)
            
            return {
                'context_scores': context_scores,
                'ambiguity': ambiguity,
                'requires_clarification': ambiguity > self.config['thresholds']['context_ambiguity']
            }
            
        except Exception as e:
            self.logger.error(f"Context analysis failed: {str(e)}")
            return {'error': str(e)}

    def _fact_check(self, content: str) -> Dict[str, Any]:
        """Fact check content.
        
        Args:
            content: Content to verify
            
        Returns:
            Fact checking results
        """
        try:
            # Generate fact check query
            query = f"Verify the factual accuracy of this statement: {content}"
            
            # Get fact check response
            response = self.fact_checker(query)[0]['generated_text']
            
            # Parse response
            accuracy = self._parse_fact_check_response(response)
            
            return {
                'accuracy': accuracy,
                'response': response,
                'requires_verification': accuracy < self.config['thresholds']['fact_accuracy']
            }
            
        except Exception as e:
            self.logger.error(f"Fact checking failed: {str(e)}")
            return {'error': str(e)}

    def _calculate_shapley_values(self, content: str) -> Dict[str, float]:
        """Calculate Shapley values for feature importance.
        
        Args:
            content: Content to analyze
            
        Returns:
            Dictionary of feature importance scores
        """
        try:
            import shap
            
            # Initialize explainer
            explainer = shap.Explainer(self.content_classifier)
            
            # Calculate Shapley values
            shap_values = explainer(content)
            
            # Convert to dictionary
            return {
                'values': shap_values.values.tolist(),
                'base_value': shap_values.base_values.tolist(),
                'data': shap_values.data
            }
            
        except Exception as e:
            self.logger.error(f"Shapley value calculation failed: {str(e)}")
            return {'error': str(e)}

    def _get_attention_weights(self, content: str) -> Dict[str, Any]:
        """Get attention weights for visualization.
        
        Args:
            content: Content to analyze
            
        Returns:
            Attention weights
        """
        try:
            # Get attention from model
            inputs = self.tokenizer(content, return_tensors="pt")
            outputs = self.model(**inputs, output_attentions=True)
            
            # Process attention weights
            attention = outputs.attentions[-1].mean(dim=1)[0]
            
            return {
                'weights': attention.tolist(),
                'tokens': self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
            }
            
        except Exception as e:
            self.logger.error(f"Attention visualization failed: {str(e)}")
            return {'error': str(e)}

    def _calculate_risk_score(self, content: str) -> float:
        """Calculate weighted risk score with context and fact checking.
        
        Args:
            content: Content to analyze
            
        Returns:
            Risk score (0-1)
        """
        try:
            # Get all scores
            content_type = self._analyze_content_type(content)
            toxicity = self._analyze_toxicity(content)
            bias = self._analyze_bias(content)
            pii = self._analyze_pii(content)
            context = self._analyze_context(content)
            fact_check = self._fact_check(content)
            
            # Calculate weighted scores
            scores = {
                'content': content_type['confidence'] * 0.8,
                'toxicity': max(p['score'] for p in toxicity['toxicity_scores']) * 1.2,
                'bias': max(p['score'] for p in bias['bias_scores']) * 0.9,
                'pii': len(pii['entities']) > 0 * 1.5,
                'context': context['ambiguity'] * 0.7,
                'fact': fact_check['accuracy'] * 1.3
            }
            
            # Apply thresholds
            thresholds = self.config.get('risk_weights', {
                'content': 0.2,
                'toxicity': 0.3,
                'bias': 0.3,
                'pii': 0.2,
                'context': 0.1,
                'fact': 0.2
            })
            
            # Calculate final score
            risk_score = sum(
                scores[k] * thresholds[k] for k in thresholds.keys()
            )
            
            return min(1.0, max(0.0, risk_score))
            
        except Exception as e:
            self.logger.error(f"Risk score calculation failed: {str(e)}")
            return 1.0  # High risk on error
        
    def _init_models(self):
        """Initialize all AI/ML models."""
        # Content Classifier
        self.content_classifier = pipeline(
            "text-classification",
            model="facebook/bart-large-mnli",
            device=-1 if not torch.cuda.is_available() else 0
        )
        
        # Toxicity Detector
        self.toxicity_detector = pipeline(
            "text-classification",
            model="facebook/roberta-hate-speech-dynabench",
            device=-1 if not torch.cuda.is_available() else 0
        )
        
        # Bias Analyzer
        self.bias_analyzer = pipeline(
            "text-classification",
            model="joeddav/xlm-roberta-large-xnli",
            device=-1 if not torch.cuda.is_available() else 0
        )
        
        # PII Detector
        self.pii_detector = pipeline(
            "token-classification",
            model="dbmdz/bert-large-cased-finetuned-conll03-english",
            device=-1 if not torch.cuda.is_available() else 0
        )
        
    def _init_pii_detector(self):
        """Initialize PII detection pipeline."""
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        }
        
    def _init_bias_analyzer(self):
        """Initialize bias analysis pipeline."""
        self.bias_categories = [
            'gender', 'race', 'age', 'religion', 'nationality',
            'sexual_orientation', 'disability', 'socioeconomic_status'
        ]
        
    def _init_toxicity_detector(self):
        """Initialize toxicity detection pipeline."""
        self.toxicity_categories = [
            'toxicity', 'severe_toxicity', 'obscene', 'threat',
            'insult', 'identity_attack', 'sexual_explicit'
        ]
        
    def _init_content_classifier(self):
        """Initialize content classification pipeline."""
        self.content_categories = [
            'technical', 'medical', 'financial', 'legal', 'educational',
            'entertainment', 'news', 'social_media', 'marketing', 'other'
        ]
        
    def analyze_content(self, content: str) -> Dict[str, Any]:
        """Comprehensive content analysis.
        
        Args:
            content: Content to analyze
            
        Returns:
            Analysis results
        """
        try:
            # Update models if needed
            self._update_models()
            
            # Run all analyses
            results = {
                'timestamp': datetime.utcnow().isoformat(),
                'content_hash': hashlib.sha256(content.encode()).hexdigest(),
                'content_analysis': self._analyze_content_type(content),
                'toxicity_analysis': self._analyze_toxicity(content),
                'bias_analysis': self._analyze_bias(content),
                'pii_analysis': self._analyze_pii(content),
                'risk_score': self._calculate_risk_score(content)
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Content analysis failed: {str(e)}")
            return {
                'error': str(e),
                'risk_score': 1.0,  # High risk on error
                'timestamp': datetime.utcnow().isoformat()
            }
            
    def _analyze_content_type(self, content: str) -> Dict[str, Any]:
        """Analyze content type and category.
        
        Args:
            content: Content to analyze
            
        Returns:
            Content type analysis
        """
        try:
            # Get category predictions
            predictions = self.content_classifier(content)
            
            # Get keyword analysis
            keywords = self._extract_keywords(content)
            
            return {
                'categories': predictions,
                'keywords': keywords,
                'confidence': max(p['score'] for p in predictions),
                'sensitive_content': self._check_sensitive_keywords(keywords)
            }
            
        except Exception as e:
            self.logger.error(f"Content type analysis failed: {str(e)}")
            return {'error': str(e)}
            
    def _analyze_toxicity(self, content: str) -> Dict[str, Any]:
        """Analyze content for toxicity and harmful content.
        
        Args:
            content: Content to analyze
            
        Returns:
            Toxicity analysis
        """
        try:
            # Get toxicity scores
            toxicity_scores = self.toxicity_detector(content)
            
            # Get sentiment analysis
            sentiment = self._analyze_sentiment(content)
            
            return {
                'toxicity_scores': toxicity_scores,
                'sentiment': sentiment,
                'requires_review': self._requires_review(toxicity_scores)
            }
            
        except Exception as e:
            self.logger.error(f"Toxicity analysis failed: {str(e)}")
            return {'error': str(e)}
            
    def _analyze_bias(self, content: str) -> Dict[str, Any]:
        """Analyze content for bias and fairness.
        
        Args:
            content: Content to analyze
            
        Returns:
            Bias analysis
        """
        try:
            # Get bias scores
            bias_scores = self.bias_analyzer(content)
            
            # Analyze representation
            representation = self._analyze_representation(content)
            
            return {
                'bias_scores': bias_scores,
                'representation': representation,
                'bias_categories': self._detect_bias_categories(content)
            }
            
        except Exception as e:
            self.logger.error(f"Bias analysis failed: {str(e)}")
            return {'error': str(e)}
            
    def _analyze_pii(self, content: str) -> Dict[str, Any]:
        """Analyze content for PII and sensitive information.
        
        Args:
            content: Content to analyze
            
        Returns:
            PII analysis
        """
        try:
            # Run PII detector
            pii_entities = self.pii_detector(content)
            
            # Check patterns
            pattern_matches = self._check_patterns(content)
            
            return {
                'entities': pii_entities,
                'pattern_matches': pattern_matches,
                'requires_masking': self._requires_masking(pii_entities, pattern_matches)
            }
            
        except Exception as e:
            self.logger.error(f"PII analysis failed: {str(e)}")
            return {'error': str(e)}
            
    def _calculate_risk_score(self, content: str) -> float:
        """Calculate overall risk score based on all analyses.
        
        Args:
            content: Content to analyze
            
        Returns:
            Risk score (0-1)
        """
        try:
            # Get all scores
            content_type = self._analyze_content_type(content)
            toxicity = self._analyze_toxicity(content)
            bias = self._analyze_bias(content)
            pii = self._analyze_pii(content)
            
            # Calculate weighted score
            scores = {
                'content': content_type['confidence'],
                'toxicity': max(p['score'] for p in toxicity['toxicity_scores']),
                'bias': max(p['score'] for p in bias['bias_scores']),
                'pii': len(pii['entities']) > 0
            }
            
            weights = self.config.get('risk_weights', {
                'content': 0.2,
                'toxicity': 0.3,
                'bias': 0.3,
                'pii': 0.2
            })
            
            risk_score = sum(
                scores[k] * weights[k] for k in weights.keys()
            )
            
            return min(1.0, max(0.0, risk_score))
            
        except Exception as e:
            self.logger.error(f"Risk score calculation failed: {str(e)}")
            return 1.0  # High risk on error
            
    def _update_models(self) -> None:
        """Update models if needed."""
        if (datetime.utcnow() - self.last_update).total_seconds() > self.update_interval:
            try:
                # Update models
                self._init_models()
                self.last_update = datetime.utcnow()
                self.logger.info("Models updated successfully")
                
            except Exception as e:
                self.logger.error(f"Failed to update models: {str(e)}")
                
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract important keywords from content.
        
        Args:
            content: Content to analyze
            
        Returns:
            List of keywords
        """
        nlp = English()
        doc = nlp(content)
        return [token.text for token in doc if token.is_stop != True and token.is_punct != True]
        
    def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze sentiment of content.
        
        Args:
            content: Content to analyze
            
        Returns:
            Sentiment analysis
        """
        sentiment_analyzer = pipeline("sentiment-analysis")
        return sentiment_analyzer(content)[0]
        
    def _analyze_representation(self, content: str) -> Dict[str, Any]:
        """Analyze representation in content.
        
        Args:
            content: Content to analyze
            
        Returns:
            Representation analysis
        """
        representation = {}
        for category in self.bias_categories:
            representation[category] = self._detect_representation(content, category)
            
        return representation
        
    def _check_sensitive_keywords(self, keywords: List[str]) -> bool:
        """Check for sensitive keywords.
        
        Args:
            keywords: List of keywords
            
        Returns:
            True if sensitive keywords detected
        """
        sensitive_keywords = self.config.get('sensitive_keywords', [])
        return any(keyword.lower() in sensitive_keywords for keyword in keywords)
        
    def _requires_review(self, scores: List[Dict[str, Any]]) -> bool:
        """Determine if content requires human review.
        
        Args:
            scores: List of score dictionaries
            
        Returns:
            True if review required
        """
        thresholds = self.config.get('review_thresholds', {
            'toxicity': 0.7,
            'bias': 0.7,
            'pii': 0.5
        })
        
        return any(
            score['score'] >= thresholds.get(category, 0.7)
            for score in scores
            for category in thresholds.keys()
        )
        
    def _detect_bias_categories(self, content: str) -> List[str]:
        """Detect bias categories in content.
        
        Args:
            content: Content to analyze
            
        Returns:
            List of detected bias categories
        """
        detected = []
        for category in self.bias_categories:
            if self._detect_bias(content, category):
                detected.append(category)
                
        return detected
        
    def _check_patterns(self, content: str) -> Dict[str, List[str]]:
        """Check for PII patterns in content.
        
        Args:
            content: Content to analyze
            
        Returns:
            Dictionary of pattern matches
        """
        matches = {}
        for pattern_name, pattern in self.pii_patterns.items():
            import re
            matches[pattern_name] = re.findall(pattern, content)
            
        return matches
        
    def _requires_masking(self, entities: List[Dict[str, Any]], pattern_matches: Dict[str, List[str]]) -> bool:
        """Determine if content requires masking.
        
        Args:
            entities: List of detected entities
            pattern_matches: Dictionary of pattern matches
            
        Returns:
            True if masking required
        """
        return bool(entities) or any(matches for matches in pattern_matches.values())
