from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AgentError(Exception):
    """Base exception for agent errors."""
    pass

class ValidationError(AgentError):
    """Raised when input validation fails."""
    pass

class ResourceError(AgentError):
    """Raised when resource allocation fails."""
    pass

class AgentTimeoutError(AgentError):
    """Raised when agent operation times out."""
    pass

class BaseAgent(ABC):
    """Base class for all Orchestratex AEM agents."""
    
    def __init__(self, name: str, role: str, capabilities: List[str], tools: Optional[List[str]] = None):
        self.name = name
        self.role = role
        self.capabilities = capabilities
        self.tools = tools or []
        self.memory = []
        self.metrics = {}
        self.error_handler = AgentErrorHandler()
        self.recovery_manager = RecoveryManager()
        
    @abstractmethod
    def perform_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific task."""
        try:
            self._validate_task(task)
            return self._execute_task(task)
        except Exception as e:
            return self.error_handler.handle_error(e, task)

    def _validate_task(self, task: Dict[str, Any]) -> None:
        """Validate task requirements."""
        if not self.validate_input(task):
            raise ValidationError(f"Invalid task format for {self.name}")
        
        required_caps = task.get("required_capabilities", [])
        if not all(cap in self.capabilities for cap in required_caps):
            raise ValidationError(f"Missing required capabilities: {required_caps}")

    def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task with error handling."""
        try:
            result = self._do_execute_task(task)
            self._log_success(task, result)
            return result
        except Exception as e:
            raise

    @abstractmethod
    def _do_execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Actual task execution logic."""
        pass

    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data format."""
        return True

    def log_activity(self, activity_type: str, details: Dict[str, Any]) -> None:
        """Log agent activities with timestamp."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agent': self.name,
            'type': activity_type,
            'details': details
        }
        self.memory.append(log_entry)

    def _log_success(self, task: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Log successful task execution."""
        self.log_activity(
            "task_success",
            {
                "task_id": task.get("id"),
                "task_type": task.get("type"),
                "result": result
            }
        )

    def _log_error(self, task: Dict[str, Any], error: Exception) -> None:
        """Log task execution error."""
        self.log_activity(
            "task_error",
            {
                "task_id": task.get("id"),
                "error_type": type(error).__name__,
                "error_message": str(error)
            }
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Retrieve agent metrics."""
        return self.metrics

    def update_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update agent metrics."""
        self.metrics.update(metrics)

    def get_capabilities(self) -> List[str]:
        """Return agent capabilities."""
        return self.capabilities

    def get_tools(self) -> List[str]:
        """Return available tools."""
        return self.tools

    def __str__(self) -> str:
        """String representation of the agent."""
        return f"Agent: {self.name}, Role: {self.role}, Capabilities: {self.capabilities}"

class AgentErrorHandler:
    def __init__(self):
        self.error_count = 0
        self.error_types = {}
        self.recovery_attempts = {}
        
    def handle_error(self, error: Exception, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle and log agent errors."""
        self.error_count += 1
        error_type = type(error).__name__
        self.error_types[error_type] = self.error_types.get(error_type, 0) + 1
        
        if error_type not in self.recovery_attempts:
            self.recovery_attempts[error_type] = 0
        
        logger.error(f"Agent error: {error_type} - {str(error)}")
        
        return {
            "error": str(error),
            "error_type": error_type,
            "task_id": task.get("id"),
            "timestamp": datetime.now().isoformat(),
            "error_id": self.error_count,
            "recovery_attempts": self.recovery_attempts[error_type]
        }

class RecoveryManager:
    def __init__(self):
        self.recovery_strategies = {
            "timeout": self._timeout_recovery,
            "resource": self._resource_recovery,
            "validation": self._validation_recovery
        }
        self.max_attempts = 3
        
    def attempt_recovery(self, error: Exception, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Attempt to recover from an error."""
        error_type = type(error).__name__
        strategy = self.recovery_strategies.get(error_type)
        
        if strategy:
            return strategy(error, task)
        return None

    def _timeout_recovery(self, error: Exception, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle timeout errors."""
        if self._get_recovery_attempts(error) < self.max_attempts:
            time.sleep(2 ** self._get_recovery_attempts(error))  # Exponential backoff
            return {"status": "retrying", "delay": 2 ** self._get_recovery_attempts(error)}
        return None

    def _resource_recovery(self, error: Exception, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle resource allocation errors."""
        # Implementation of resource recovery
        return None

    def _validation_recovery(self, error: Exception, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle validation errors."""
        # Implementation of validation recovery
        return None

    def _get_recovery_attempts(self, error: Exception) -> int:
        """Get number of recovery attempts for an error type."""
        error_type = type(error).__name__
        return self.recovery_attempts.get(error_type, 0)
