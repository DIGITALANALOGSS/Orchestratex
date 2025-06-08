import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import os
from ..config import ConfigManager

class EnvironmentManager:
    def __init__(self):
        """Initialize environment manager."""
        self.logger = logging.getLogger(__name__)
        self.config_manager = ConfigManager()
        self.environments = {
            "dev": "development",
            "staging": "staging",
            "prod": "production"
        }
        self.current_env = None
        self.config = None
        self._load_environment()
        
    def _load_environment(self):
        """Load current environment configuration."""
        try:
            env = os.getenv("ORCHESTRATEX_ENV", "dev")
            if env not in self.environments:
                self.logger.warning(f"Invalid environment: {env}. Using 'dev' as default")
                env = "dev"
                
            self.current_env = env
            config_path = Path(f"environments/{env}/config.yaml")
            
            if not config_path.exists():
                self.logger.error(f"Config file not found: {config_path}")
                return
                
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
                
            self.logger.info(f"Loaded environment: {env}")
            
        except Exception as e:
            self.logger.error(f"Failed to load environment: {str(e)}")
            
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        try:
            if not self.config:
                return default
                
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
                    
            return value
            
        except Exception as e:
            self.logger.error(f"Failed to get config {key}: {str(e)}")
            return default
            
    def set_config(self, key: str, value: Any) -> bool:
        """Set configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
            
        Returns:
            True if set successfully
        """
        try:
            if not self.config:
                return False
                
            keys = key.split('.')
            current = self.config
            
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
                
            current[keys[-1]] = value
            
            # Save updated config
            self._save_config()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set config {key}: {str(e)}")
            return False
            
    def _save_config(self):
        """Save configuration to file."""
        try:
            config_path = Path(f"environments/{self.current_env}/config.yaml")
            with open(config_path, 'w') as f:
                yaml.dump(self.config, f)
            
        except Exception as e:
            self.logger.error(f"Failed to save config: {str(e)}")
            
    def get_environment(self) -> str:
        """Get current environment.
        
        Returns:
            Current environment name
        """
        return self.current_env
        
    def get_all_environments(self) -> Dict[str, str]:
        """Get all available environments.
        
        Returns:
            Dictionary of environment names and descriptions
        """
        return self.environments
        
    def is_production(self) -> bool:
        """Check if current environment is production.
        
        Returns:
            True if production environment
        """
        return self.current_env == "prod"
        
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration.
        
        Returns:
            Database configuration dictionary
        """
        return self.config.get("database", {})
        
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration.
        
        Returns:
            API configuration dictionary
        """
        return self.config.get("api", {})
        
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration.
        
        Returns:
            Security configuration dictionary
        """
        return self.config.get("security", {})
        
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration.
        
        Returns:
            Monitoring configuration dictionary
        """
        return self.config.get("monitoring", {})
        
    def get_content_config(self) -> Dict[str, Any]:
        """Get content management configuration.
        
        Returns:
            Content management configuration dictionary
        """
        return self.config.get("content", {})
        
    def get_quantum_config(self) -> Dict[str, Any]:
        """Get quantum computing configuration.
        
        Returns:
            Quantum computing configuration dictionary
        """
        return self.config.get("quantum", {})
        
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI configuration.
        
        Returns:
            AI configuration dictionary
        """
        return self.config.get("ai", {})
        
    def get_deployment_config(self) -> Dict[str, Any]:
        """Get deployment configuration.
        
        Returns:
            Deployment configuration dictionary
        """
        return self.config.get("deployment", {})
        
    def validate_config(self) -> bool:
        """Validate current configuration.
        
        Returns:
            True if configuration is valid
        """
        try:
            # Basic validation
            required_keys = [
                "environment",
                "version",
                "database",
                "api",
                "security",
                "monitoring",
                "content",
                "quantum",
                "ai",
                "deployment"
            ]
            
            for key in required_keys:
                if key not in self.config:
                    self.logger.error(f"Missing required config: {key}")
                    return False
                    
            # Validate specific configurations
            if not self.config["database"]["host"]:
                self.logger.error("Missing database host")
                return False
                
            if not self.config["api"]["port"]:
                self.logger.error("Missing API port")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate config: {str(e)}")
            return False
