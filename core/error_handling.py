import logging
import traceback
from typing import Optional, Dict, Any
import json
from datetime import datetime
import uuid

class OrchestratexError(Exception):
    """Base exception for all Orchestratex errors."""
    def __init__(self, 
                 message: str, 
                 error_code: str, 
                 details: Optional[Dict[str, Any]] = None,
                 cause: Optional[Exception] = None):
        """
        Initialize an Orchestratex error.
        
        Args:
            message: Error message
            error_code: Unique error code
            details: Additional error details
            cause: Original exception that caused this error
        """
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.cause = cause
        self.timestamp = datetime.utcnow()
        self.error_id = str(uuid.uuid4())
        
        super().__init__(self.format_error())

    def format_error(self) -> str:
        """Format the error as a string."""
        error_data = {
            "error_id": self.error_id,
            "timestamp": self.timestamp.isoformat(),
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }
        
        if self.cause:
            error_data["cause"] = {
                "type": type(self.cause).__name__,
                "message": str(self.cause)
            }
            
        return json.dumps(error_data, indent=2)

class ConfigurationError(OrchestratexError):
    """Raised when there's a configuration issue."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="CONFIG_ERROR",
            details=details
        )

class AuthenticationError(OrchestratexError):
    """Raised when authentication fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTH_ERROR",
            details=details
        )

class ResourceNotFoundError(OrchestratexError):
    """Raised when a required resource is not found."""
    def __init__(self, message: str, resource_type: str, resource_id: str):
        super().__init__(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            details={
                "resource_type": resource_type,
                "resource_id": resource_id
            }
        )

class ValidationError(OrchestratexError):
    """Raised when input validation fails."""
    def __init__(self, message: str, field: str, value: Any):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details={
                "field": field,
                "value": str(value)
            }
        )

class SystemError(OrchestratexError):
    """Raised for system-level errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="SYSTEM_ERROR",
            details=details
        )

class ErrorHandler:
    """Central error handling and reporting system."""
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_queue = []
        
    def handle_error(self, error: Exception):
        """Handle and log an error."""
        if isinstance(error, OrchestratexError):
            self.logger.error(
                f"Error ID: {error.error_id}\n"
                f"Error Code: {error.error_code}\n"
                f"Message: {error.message}\n"
                f"Details: {json.dumps(error.details, indent=2)}\n"
                f"Timestamp: {error.timestamp.isoformat()}"
            )
        else:
            error_id = str(uuid.uuid4())
            self.logger.error(
                f"Error ID: {error_id}\n"
                f"Error Type: {type(error).__name__}\n"
                f"Message: {str(error)}\n"
                f"Traceback: {traceback.format_exc()}"
            )
        
        self.error_queue.append(error)
        
    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of all errors."""
        return {
            "total_errors": len(self.error_queue),
            "error_types": {
                type(err).__name__: sum(
                    1 for err in self.error_queue 
                    if isinstance(err, type(err))
                )
                for err in self.error_queue
            },
            "latest_errors": [
                {
                    "error_id": err.error_id if hasattr(err, 'error_id') else str(uuid.uuid4()),
                    "timestamp": err.timestamp.isoformat() if hasattr(err, 'timestamp') else datetime.utcnow().isoformat(),
                    "error_type": type(err).__name__
                }
                for err in self.error_queue[-5:]  # Last 5 errors
            ]
        }

class ErrorReporter:
    """Error reporting system for external services."""
    def __init__(self):
        self.error_handler = ErrorHandler()
        
    def report_to_sentry(self, error: Exception):
        """Report error to Sentry."""
        try:
            import sentry_sdk
            sentry_sdk.capture_exception(error)
        except ImportError:
            self.error_handler.handle_error(
                SystemError("Sentry SDK not installed", "SDK_ERROR")
            )
        except Exception as e:
            self.error_handler.handle_error(
                SystemError(f"Failed to report to Sentry: {str(e)}", "REPORT_ERROR")
            )

    def report_to_datadog(self, error: Exception):
        """Report error to Datadog."""
        try:
            from datadog import initialize, statsd
            initialize()
            statsd.increment('orchestratex.errors.total')
        except ImportError:
            self.error_handler.handle_error(
                SystemError("Datadog SDK not installed", "SDK_ERROR")
            )
        except Exception as e:
            self.error_handler.handle_error(
                SystemError(f"Failed to report to Datadog: {str(e)}", "REPORT_ERROR")
            )

def setup_error_handling():
    """Setup global error handling."""
    error_reporter = ErrorReporter()
    
    def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        error_reporter.error_handler.handle_error(exc_value)
        error_reporter.report_to_sentry(exc_value)
        error_reporter.report_to_datadog(exc_value)
        
    sys.excepthook = handle_uncaught_exception
    
    return error_reporter
