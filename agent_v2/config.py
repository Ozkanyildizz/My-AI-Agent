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
        self._validate_api_keys_and_models()
        self.max_history = self._get_int_env("MAX_HISTORY", 20)
        self.history_keep = self._get_int_env("HISTORY_KEEP", 10)
        self.temperature = self._get_float_env("TEMPERATURE", 0.2)
        self.tasks_dir = os.getenv("TASKS_DIR", "tasks")
        self.lessons_file = os.path.join(self.tasks_dir, "lessons.md")
        
        logger.info(f"Configuration loaded: model={self.model}, max_history={self.max_history}")
    
    def _validate_api_keys_and_models(self) -> None:
        """Validate API keys and set up model-related configurations."""
        self.api_key = os.getenv("GROQ_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        # Determine active model provider
        # If user explicitly sets ACTIVE_MODEL, use it. Otherwise default to 'groq'
        # unless only Gemini key is present.
        self.active_provider = os.getenv("ACTIVE_PROVIDER", "groq").lower()
        
        if not self.api_key and not self.gemini_api_key:
            raise ConfigurationError(
                "No API keys found! Please set GROQ_API_KEY or GEMINI_API_KEY in .env. "
                "Please create a .env file with your API key."
            )
        
        # Adjust active_provider if only one key is present
        if self.api_key and not self.gemini_api_key and self.active_provider != "groq":
            logger.warning(f"GROQ_API_KEY is present but GEMINI_API_KEY is not. Forcing active_provider to 'groq'.")
            self.active_provider = "groq"
        elif not self.api_key and self.gemini_api_key and self.active_provider != "gemini":
            logger.warning(f"GEMINI_API_KEY is present but GROQ_API_KEY is not. Forcing active_provider to 'gemini'.")
            self.active_provider = "gemini"
        elif self.api_key and self.gemini_api_key and self.active_provider not in ["groq", "gemini"]:
            logger.warning(f"Invalid ACTIVE_PROVIDER '{self.active_provider}'. Defaulting to 'groq'.")
            self.active_provider = "groq"
            
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
