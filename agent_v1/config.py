"""Configuration management for the AI Engineer application."""

import os
import logging
from typing import Optional
from dotenv import load_dotenv
from exceptions import ConfigurationError


# Load environment variables
load_dotenv()

# Setup logging - write to file only, not console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='ai_agent.log',
    filemode='a'
)
logger = logging.getLogger(__name__)


class Config:
    """Application configuration with validation."""
    
    def __init__(self):
        """Initialize and validate configuration."""
        self.api_key = self._validate_api_key()
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.max_history = self._get_int_env("MAX_HISTORY", 20)
        self.history_keep = self._get_int_env("HISTORY_KEEP", 10)
        self.temperature = self._get_float_env("TEMPERATURE", 0.2)
        self.tasks_dir = os.getenv("TASKS_DIR", "tasks")
        self.lessons_file = os.path.join(self.tasks_dir, "lessons.md")
        
        logger.info(f"Configuration loaded: model={self.model}, max_history={self.max_history}")
    
    def _validate_api_key(self) -> str:
        """Validate and return API key."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ConfigurationError(
                "GROQ_API_KEY not found in environment variables. "
                "Please create a .env file with your API key."
            )
        return api_key
    
    def _get_int_env(self, key: str, default: int) -> int:
        """Get integer environment variable with validation."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            logger.warning(f"Invalid integer for {key}: {value}, using default: {default}")
            return default
    
    def _get_float_env(self, key: str, default: float) -> float:
        """Get float environment variable with validation."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            logger.warning(f"Invalid float for {key}: {value}, using default: {default}")
            return default
