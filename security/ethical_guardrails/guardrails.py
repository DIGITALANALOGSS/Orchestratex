import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime
import hashlib
import json
from .ai_analyzer import AIAnalyzer
from .audit import AuditLogger
from .policy_manager import PolicyManager

class EthicalGuardrails:
    def __init__(self, config: Dict[str, Any]):
        """Initialize the ethical guardrails system.
        
        Args:
            config: Configuration dictionary containing:
                - keywords: List of blocked and approved keywords
                - ai_config: AI/ML configuration
                - audit_config: Audit logging configuration
                - policy_config: Policy management configuration
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Initialize components
        self.ai_analyzer = AIAnalyzer(config.get('ai_config', {}))
        self.audit_logger = AuditLogger(config.get('audit_config', {}))
        self.policy_manager = PolicyManager(config.get('policy_config', {}))
        
        # Load keyword lists
        self.blocked_keywords = self._load_keyword_list('blocked')
        self.approved_actions = self._load_keyword_list('approved')
        self.suspicious_keywords = self._load_keyword_list('suspicious')
        
    def _load_keyword_list(self, keyword_type: str) -> List[str]:
        """Load keyword list from configuration or defaults.
        
        Args:
            keyword_type: Type of keyword list ('blocked', 'approved', 'suspicious')
            
        Returns:
            List of keywords
        """
        default_lists = {
            'blocked': [
                'illegal', 'harm', 'destroy', 'corrupt', 'attack', 'exploit', 'weapon', 'malware',
                'ransomware', 'bypass', 'hack', 'violence', 'terror', 'abuse', 'discriminate',
                'scam', 'phishing', 'fraud'
            ],
            'approved': [
                'create', 'learn', 'collaborate', 'build', 'educate', 'help', 'mentor', 'optimize',
                'analyze', 'develop', 'innovate', 'improve', 'support', 'assist'
            ],
            'suspicious': [
                'hack', 'bypass', 'exploit', 'weapon', 'override', 'inject', 'rootkit', 'backdoor',
                'exploit', 'malicious', 'attack', 'vulnerability', 'security', 'password', 'credential'
            ]
        }
        
        return self.config.get(f'{keyword_type}_keywords', default_lists[keyword_type])
        
    def content_filter(self, content: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Filter content using multiple layers of security.
        
        Args:
            content: Content to filter
            
        Returns:
            Tuple of (is_approved, reason, metadata)
        """
        try:
            # Basic keyword filtering
            keyword_check = self._basic_keyword_filter(content)
            if not keyword_check['approved']:
                return False, keyword_check['reason'], keyword_check
                
            # AI/ML analysis
            ai_analysis = self.ai_analyzer.analyze_content(content)
            if ai_analysis['risk_score'] > self.config.get('ai_threshold', 0.7):
                return False, 'Content flagged by AI analysis', ai_analysis
                
            # Policy check
            policy_check = self.policy_manager.check_policy(content)
            if not policy_check['approved']:
                return False, policy_check['reason'], policy_check
                
            # Generate metadata
            metadata = {
                'timestamp': datetime.utcnow().isoformat(),
                'content_hash': hashlib.sha256(content.encode()).hexdigest(),
                'ai_analysis': ai_analysis,
                'keyword_check': keyword_check,
                'policy_check': policy_check
            }
            
            return True, 'Content approved', metadata
            
        except Exception as e:
            self.logger.error(f"Content filtering failed: {str(e)}")
            return False, f'Error during content filtering: {str(e)}', {'error': str(e)}
            
    def _basic_keyword_filter(self, content: str) -> Dict[str, Any]:
        """Basic keyword-based filtering.
        
        Args:
            content: Content to filter
            
        Returns:
            Filter results
        """
        content_lower = content.lower()
        
        # Check blocked keywords
        for word in self.blocked_keywords:
            if word in content_lower:
                return {
                    'approved': False,
                    'reason': f'Blocked keyword detected: {word}',
                    'type': 'blocked_keyword',
                    'keyword': word
                }
                
        # Check approved actions
        if not any(word in content_lower for word in self.approved_actions):
            return {
                'approved': False,
                'reason': 'No approved actions detected',
                'type': 'no_approved_action'
            }
            
        return {
            'approved': True,
            'reason': 'Basic keyword check passed',
            'type': 'passed'
        }
        
    def action_check(self, action: str, context: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Check if an action is allowed based on context.
        
        Args:
            action: Action to check
            context: Context information
            
        Returns:
            Tuple of (is_allowed, reason, metadata)
        """
        try:
            # Basic action validation
            if action.lower() not in self.approved_actions:
                return False, f'Action "{action}" is not allowed', {
                    'type': 'invalid_action',
                    'action': action
                }
                
            # Context-based validation
            context_check = self._validate_context(action, context)
            if not context_check['approved']:
                return False, context_check['reason'], context_check
                
            # Policy validation
            policy_check = self.policy_manager.check_action_policy(action, context)
            if not policy_check['approved']:
                return False, policy_check['reason'], policy_check
                
            return True, 'Action approved', {
                'timestamp': datetime.utcnow().isoformat(),
                'action': action,
                'context_check': context_check,
                'policy_check': policy_check
            }
            
        except Exception as e:
            self.logger.error(f"Action check failed: {str(e)}")
            return False, f'Error during action check: {str(e)}', {'error': str(e)}
            
    def _validate_context(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate action context.
        
        Args:
            action: Action being performed
            context: Context information
            
        Returns:
            Validation results
        """
        # Basic context validation
        if not context:
            return {
                'approved': False,
                'reason': 'No context provided',
                'type': 'no_context'
            }
            
        # Check for suspicious patterns
        suspicious_count = sum(1 for word in self.suspicious_keywords 
                             if word.lower() in json.dumps(context).lower())
        
        if suspicious_count > self.config.get('suspicious_threshold', 2):
            return {
                'approved': False,
                'reason': 'Suspicious context detected',
                'type': 'suspicious_context',
                'suspicious_count': suspicious_count
            }
            
        return {
            'approved': True,
            'reason': 'Context validation passed',
            'type': 'passed'
        }
        
    def human_review_required(self, content: str, metadata: Dict[str, Any]) -> bool:
        """Determine if human review is required.
        
        Args:
            content: Content to review
            metadata: Analysis metadata
            
        Returns:
            True if human review is required
        """
        content_lower = content.lower()
        
        # Check suspicious keywords
        if any(word in content_lower for word in self.suspicious_keywords):
            return True
            
        # Check AI risk score
        if metadata.get('ai_analysis', {}).get('risk_score', 0) > 0.5:
            return True
            
        # Check policy flags
        if metadata.get('policy_check', {}).get('requires_review', False):
            return True
            
        return False
        
    def audit_log(self, user_id: str, action: str, content: str, 
                 decision: str, metadata: Dict[str, Any]) -> None:
        """Log audit trail for transparency.
        
        Args:
            user_id: User identifier
            action: Action performed
            content: Content processed
            decision: Decision made
            metadata: Analysis metadata
        """
        try:
            audit_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': user_id,
                'action': action,
                'content_hash': hashlib.sha256(content.encode()).hexdigest(),
                'decision': decision,
                'metadata': metadata
            }
            
            self.audit_logger.log(audit_data)
            
        except Exception as e:
            self.logger.error(f"Audit logging failed: {str(e)}")
