import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self, config_path: str = "config/agents.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._validate_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML: {e}")
            raise

    def _validate_config(self) -> None:
        """Validate configuration structure."""
        required_keys = ["agents", "orchestrator", "security"]
        missing_keys = [k for k in required_keys if k not in self.config]
        
        if missing_keys:
            raise ValueError(f"Missing required config keys: {missing_keys}")

    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get configuration for a specific agent."""
        return self.config["agents"].get(agent_name, {})

    def get_orchestrator_config(self) -> Dict[str, Any]:
        """Get orchestrator configuration."""
        return self.config["orchestrator"]

    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        return self.config["security"]

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update configuration and save to file."""
        self.config.update(new_config)
        self._validate_config()
        self._save_config()

    def _save_config(self) -> None:
        """Save configuration to YAML file."""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            raise

    def get_model_config(self, agent_name: str) -> Dict[str, Any]:
        """Get model configuration for a specific agent."""
        agent_config = self.get_agent_config(agent_name)
        return agent_config.get("model", {})

    def get_tool_config(self, agent_name: str, tool_name: str) -> Dict[str, Any]:
        """Get configuration for a specific agent's tool."""
        agent_config = self.get_agent_config(agent_name)
        tools = agent_config.get("tools", {})
        return tools.get(tool_name, {})
