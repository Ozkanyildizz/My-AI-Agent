"""Custom exceptions for the AI Engineer application."""


class AIEngineerError(Exception):
    """Base exception for all AI Engineer errors."""
    pass


class FileReadError(AIEngineerError):
    """Exception raised when file reading fails."""
    
    def __init__(self, file_path: str, reason: str):
        self.file_path = file_path
        self.reason = reason
        super().__init__(f"Failed to read file '{file_path}': {reason}")


class APIError(AIEngineerError):
    """Exception raised when API calls fail."""
    
    def __init__(self, message: str, error_type: str = "unknown"):
        self.error_type = error_type
        super().__init__(message)


class ConfigurationError(AIEngineerError):
    """Exception raised when configuration is invalid."""
    
    def __init__(self, message: str):
        super().__init__(f"Configuration error: {message}")
