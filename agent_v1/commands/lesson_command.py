"""Lesson logging command handler."""

import datetime
import logging

logger = logging.getLogger(__name__)


class LessonCommand:
    """Handler for lesson: command to log lessons learned."""
    
    def __init__(self, config):
        """Initialize lesson command handler.
        
        Args:
            config: Application configuration object
        """
        self.config = config
        self.lessons_file = config.lessons_file
    
    def log(self, lesson_text: str) -> str:
        """
        Log a lesson learned for future reference.
        
        Args:
            lesson_text: The lesson to log
            
        Returns:
            Success message with file path
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            with open(self.lessons_file, "a", encoding="utf-8") as f:
                f.write(f"- [{timestamp}]: {lesson_text}\n")
            logger.info(f"Logged lesson: {lesson_text[:50]}...")
            return f"Successfully logged to {self.lessons_file}"
        except Exception as e:
            logger.error(f"Failed to log lesson: {e}")
            return f"Error logging lesson: {str(e)}"
