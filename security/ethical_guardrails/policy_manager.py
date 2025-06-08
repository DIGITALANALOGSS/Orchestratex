import logging
from typing import Dict, Any, List, Tuple
import json
import hashlib
from datetime import datetime
import os
from pathlib import Path

class PolicyManager:
    def __init__(self, config: Dict[str, Any]):
        """Initialize policy manager.
        
        Args:
            config: Configuration dictionary containing:
                - policy_dir: Directory for policy files
                - policy_types: Types of policies to enforce
                - enforcement_level: Strictness level
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Initialize policies
        self.policy_dir = Path(config.get('policy_dir', 'policies'))
        self.policy_types = config.get('policy_types', ['content', 'action', 'context'])
        self.enforcement_level = config.get('enforcement_level', 'strict')
        
        # Load policies
        self.policies = self._load_policies()
        
    def _load_policies(self) -> Dict[str, Any]:
        """Load policies from configuration directory.
        
        Returns:
            Dictionary of loaded policies
        """
        policies = {}
        
        if not self.policy_dir.exists():
            self.policy_dir.mkdir(parents=True)
            
        for policy_type in self.policy_types:
            policy_path = self.policy_dir / f"{policy_type}_policy.json"
            if policy_path.exists():
                try:
                    with open(policy_path) as f:
                        policies[policy_type] = json.load(f)
                except Exception as e:
                    self.logger.error(f"Failed to load {policy_type} policy: {str(e)}")
                    policies[policy_type] = {}
            else:
                policies[policy_type] = self._create_default_policy(policy_type)
                
        return policies
        
    def _create_default_policy(self, policy_type: str) -> Dict[str, Any]:
        """Create default policy for a given type.
        
        Args:
            policy_type: Type of policy
            
        Returns:
            Default policy dictionary
        """
        defaults = {
            'content': {
                'blocked_keywords': [],
                'approved_keywords': [],
                'max_length': 10000,
                'min_length': 10
            },
            'action': {
                'allowed_actions': [],
                'blocked_actions': [],
                'context_requirements': {}
            },
            'context': {
                'required_fields': [],
                'validation_rules': {},
                'suspicious_patterns': []
            }
        }
        
        return defaults.get(policy_type, {})
        
    def check_policy(self, content: str) -> Dict[str, Any]:
        """Check content against policies.
        
        Args:
            content: Content to check
            
        Returns:
            Policy check results
        """
        try:
            # Check content policy
            content_check = self._check_content_policy(content)
            if not content_check['approved']:
                return content_check
                
            # Check length
            length_check = self._check_length(content)
            if not length_check['approved']:
                return length_check
                
            return {
                'approved': True,
                'reason': 'Policy check passed',
                'type': 'passed',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Policy check failed: {str(e)}")
            return {
                'approved': False,
                'reason': f'Error during policy check: {str(e)}',
                'type': 'error'
            }
            
    def check_action_policy(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check action against policies.
        
        Args:
            action: Action to check
            context: Context information
            
        Returns:
            Policy check results
        """
        try:
            # Check allowed actions
            if action.lower() not in self.policies['action'].get('allowed_actions', []):
                return {
                    'approved': False,
                    'reason': f'Action "{action}" is not allowed',
                    'type': 'invalid_action'
                }
                
            # Check blocked actions
            if action.lower() in self.policies['action'].get('blocked_actions', []):
                return {
                    'approved': False,
                    'reason': f'Action "{action}" is blocked',
                    'type': 'blocked_action'
                }
                
            # Check context requirements
            context_check = self._check_context_policy(context)
            if not context_check['approved']:
                return context_check
                
            return {
                'approved': True,
                'reason': 'Action policy check passed',
                'type': 'passed',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Action policy check failed: {str(e)}")
            return {
                'approved': False,
                'reason': f'Error during action policy check: {str(e)}',
                'type': 'error'
            }
            
    def _check_content_policy(self, content: str) -> Dict[str, Any]:
        """Check content against content policy.
        
        Args:
            content: Content to check
            
        Returns:
            Policy check results
        """
        content_policy = self.policies.get('content', {})
        
        # Check blocked keywords
        for keyword in content_policy.get('blocked_keywords', []):
            if keyword.lower() in content.lower():
                return {
                    'approved': False,
                    'reason': f'Blocked keyword detected: {keyword}',
                    'type': 'blocked_keyword'
                }
                
        # Check approved keywords
        if content_policy.get('approved_keywords'):
            approved = False
            for keyword in content_policy['approved_keywords']:
                if keyword.lower() in content.lower():
                    approved = True
                    break
                    
            if not approved:
                return {
                    'approved': False,
                    'reason': 'No approved keywords detected',
                    'type': 'no_approved_keyword'
                }
                
        return {
            'approved': True,
            'reason': 'Content policy check passed',
            'type': 'passed'
        }
        
    def _check_length(self, content: str) -> Dict[str, Any]:
        """Check content length against policy.
        
        Args:
            content: Content to check
            
        Returns:
            Length check results
        """
        content_policy = self.policies.get('content', {})
        
        content_length = len(content)
        max_length = content_policy.get('max_length', 10000)
        min_length = content_policy.get('min_length', 10)
        
        if content_length > max_length:
            return {
                'approved': False,
                'reason': f'Content too long (max {max_length} characters)',
                'type': 'too_long'
            }
            
        if content_length < min_length:
            return {
                'approved': False,
                'reason': f'Content too short (min {min_length} characters)',
                'type': 'too_short'
            }
            
        return {
            'approved': True,
            'reason': 'Length check passed',
            'type': 'passed'
        }
        
    def _check_context_policy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check context against policy.
        
        Args:
            context: Context information
            
        Returns:
            Context check results
        """
        context_policy = self.policies.get('context', {})
        
        # Check required fields
        for field in context_policy.get('required_fields', []):
            if field not in context:
                return {
                    'approved': False,
                    'reason': f'Required field missing: {field}',
                    'type': 'missing_field'
                }
                
        # Check validation rules
        for field, rules in context_policy.get('validation_rules', {}).items():
            if field in context:
                value = context[field]
                for rule in rules:
                    if not self._validate_rule(value, rule):
                        return {
                            'approved': False,
                            'reason': f'Field {field} failed validation: {rule}',
                            'type': 'validation_failed'
                        }
                        
        return {
            'approved': True,
            'reason': 'Context check passed',
            'type': 'passed'
        }
        
    def _validate_rule(self, value: Any, rule: Dict[str, Any]) -> bool:
        """Validate a value against a rule.
        
        Args:
            value: Value to validate
            rule: Validation rule
            
        Returns:
            True if validation passes
        """
        rule_type = rule.get('type')
        
        if rule_type == 'length':
            min_length = rule.get('min', 0)
            max_length = rule.get('max', float('inf'))
            return min_length <= len(str(value)) <= max_length
            
        elif rule_type == 'pattern':
            pattern = rule.get('pattern', '')
            import re
            return bool(re.match(pattern, str(value)))
            
        elif rule_type == 'enum':
            allowed_values = rule.get('values', [])
            return value in allowed_values
            
        return True  # Default to pass if rule type not recognized
