import functools
from typing import Callable, Any
from .progress_manager import ProgressManager

class ProgressDecorator:
    def __init__(self):
        """Initialize progress decorator."""
        self.progress_manager = ProgressManager()
        
    def save_progress(self, func: Callable) -> Callable:
        """Decorator to save progress after function execution.
        
        Args:
            func: Function to decorate
            
        Returns:
            Decorated function
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Save progress
                self.progress_manager.save_progress()
                
                return result
                
            except Exception as e:
                self.progress_manager.logger.error(f"Function {func.__name__} failed: {str(e)}")
                raise
                
        return wrapper
        
    def track_user_progress(self, user_id: str) -> Callable:
        """Decorator to track user progress.
        
        Args:
            user_id: User ID to track
            
        Returns:
            Decorated function
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                try:
                    # Execute the function
                    result = func(*args, **kwargs)
                    
                    # Track progress
                    progress_data = {
                        "function": func.__name__,
                        "timestamp": datetime.now().isoformat(),
                        "args": str(args),
                        "kwargs": str(kwargs)
                    }
                    self.progress_manager.add_user_progress(user_id, progress_data)
                    
                    return result
                    
                except Exception as e:
                    self.progress_manager.logger.error(f"Function {func.__name__} failed: {str(e)}")
                    raise
                    
            return wrapper
            
        return decorator
        
    def track_project_progress(self, project_id: str) -> Callable:
        """Decorator to track project progress.
        
        Args:
            project_id: Project ID to track
            
        Returns:
            Decorated function
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                try:
                    # Execute the function
                    result = func(*args, **kwargs)
                    
                    # Track progress
                    progress_data = {
                        "function": func.__name__,
                        "timestamp": datetime.now().isoformat(),
                        "args": str(args),
                        "kwargs": str(kwargs)
                    }
                    self.progress_manager.add_project_progress(project_id, progress_data)
                    
                    return result
                    
                except Exception as e:
                    self.progress_manager.logger.error(f"Function {func.__name__} failed: {str(e)}")
                    raise
                    
            return wrapper
            
        return decorator
        
    def track_session(self) -> Callable:
        """Decorator to track session progress.
        
        Returns:
            Decorated function
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                try:
                    # Execute the function
                    result = func(*args, **kwargs)
                    
                    # Track session
                    progress_data = {
                        "function": func.__name__,
                        "timestamp": datetime.now().isoformat(),
                        "args": str(args),
                        "kwargs": str(kwargs)
                    }
                    self.progress_manager.add_session_data(progress_data)
                    
                    return result
                    
                except Exception as e:
                    self.progress_manager.logger.error(f"Function {func.__name__} failed: {str(e)}")
                    raise
                    
            return wrapper
            
        return decorator
