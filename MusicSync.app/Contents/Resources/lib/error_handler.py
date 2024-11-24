# error_handler.py
import logging
import functools
import traceback
from typing import Callable, Any, Type
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class MusicSyncError(Exception):
    """Base exception class for the application"""
    pass

class TagError(MusicSyncError):
    """Tag reading/writing errors"""
    pass

class DatabaseError(MusicSyncError):
    """Database operation errors"""
    pass

class FileSystemError(MusicSyncError):
    """File system operation errors"""
    pass

def log_error(func: Callable) -> Callable:
    """Decorator for error logging and handling"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Get function context
            module = func.__module__
            name = func.__name__
            
            # Log the error with stack trace
            logging.error(
                f"Error in {module}.{name}: {str(e)}\n"
                f"Args: {args}, Kwargs: {kwargs}\n"
                f"Stack trace:\n{traceback.format_exc()}"
            )
            
            # Re-raise with additional context
            raise type(e)(f"{str(e)} in {module}.{name}") from e
    return wrapper

def handle_database_error(func: Callable) -> Callable:
    """Specific decorator for database operations"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Database error in {func.__name__}: {str(e)}")
            raise DatabaseError(f"Database operation failed: {str(e)}") from e
    return wrapper

class ErrorLogger:
    """Central error logging and handling"""
    
    def __init__(self):
        self.error_log = []
        
    def log_error(self, error: Exception, context: str = None):
        """Log an error with context"""
        error_entry = {
            'timestamp': datetime.now(),
            'error': str(error),
            'type': type(error).__name__,
            'context': context,
            'traceback': traceback.format_exc()
        }
        self.error_log.append(error_entry)
        logging.error(f"Error in {context}: {str(error)}")
        
    def get_recent_errors(self, count: int = 10):
        """Get most recent errors"""
        return self.error_log[-count:]
        
    def clear_log(self):
        """Clear error log"""
        self.error_log.clear()

# Global error logger instance
error_logger = ErrorLogger()