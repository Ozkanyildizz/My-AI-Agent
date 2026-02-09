"""File reading command handler."""

import os
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class ReadCommand:
    """Handler for read: command to analyze code files."""
    
    def __init__(self, config):
        """Initialize read command handler.
        
        Args:
            config: Application configuration object
        """
        self.config = config
    
    def read_file_content(self, file_path: str) -> str:
        """
        Read file content with support for relative, absolute, and ~ paths.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            File content wrapped with markers, or error message with [FILE_READ_ERROR] prefix
        """
        try:
            # Expand ~ to home directory and convert to absolute path
            expanded_path = os.path.expanduser(file_path)
            absolute_path = os.path.abspath(expanded_path)
            
            # Check if file exists
            if not os.path.exists(absolute_path):
                error_msg = (
                    f"\033[91mError: File not found: {file_path}\033[0m\n"
                    f"Tried absolute path: {absolute_path}\n"
                    f"Please check the file path and try again."
                )
                logger.warning(f"File not found: {absolute_path}")
                return f"[FILE_READ_ERROR]{error_msg}"
            
            # Check if it's a file (not a directory)
            if not os.path.isfile(absolute_path):
                logger.warning(f"Path is not a file: {absolute_path}")
                return f"[FILE_READ_ERROR]\033[91mError: Path is not a file: {file_path}\033[0m"
            
            # Read file content
            with open(absolute_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            logger.info(f"Successfully read file: {absolute_path} ({len(content)} chars)")
            return f"\n--- FILE CONTENT ({absolute_path}) ---\n{content}\n--- END OF FILE ---"
            
        except PermissionError:
            logger.error(f"Permission denied: {file_path}")
            return f"[FILE_READ_ERROR]\033[91mError: Permission denied to read file: {file_path}\033[0m"
        except UnicodeDecodeError:
            logger.error(f"Encoding error: {file_path}")
            return f"[FILE_READ_ERROR]\033[91mError: File is not a text file or encoding issue: {file_path}\033[0m"
        except Exception as e:
            logger.error(f"Unexpected error reading file {file_path}: {e}")
            return f"[FILE_READ_ERROR]\033[91mError reading file: {str(e)}\033[0m"
    
    def parse_command(self, user_input: str) -> Optional[Tuple[str, str]]:
        """
        Parse 'read:' command to extract file path and user prompt.
        
        Args:
            user_input: User's input string
            
        Returns:
            Tuple of (file_path, user_prompt) if command found, None otherwise
        """
        if "read:" not in user_input.lower():
            return None
        
        # Find the position of "read:" (case-insensitive)
        read_pos = user_input.lower().find("read:")
        after_read = user_input[read_pos + 5:].strip()
        
        # Extract file path (first word/token)
        if not after_read:
            logger.warning("Empty read: command")
            return None
        
        potential_file = after_read.split()[0].rstrip('.')
        user_prompt = after_read[len(potential_file):].strip()
        
        if not user_prompt:
            user_prompt = "Analyze this file in detail."
        
        logger.debug(f"Parsed read command: file={potential_file}, prompt={user_prompt[:30]}...")
        return potential_file, user_prompt
    
    def process(self, file_path: str, user_prompt: str) -> Tuple[bool, str]:
        """
        Process file reading and prepare for conversation.
        
        Args:
            file_path: Path to file to read
            user_prompt: User's analysis prompt
            
        Returns:
            Tuple of (success: bool, message: str)
            - If success: message is the formatted user input
            - If error: message is the error text
        """
        file_data = self.read_file_content(file_path)
        
        if file_data.startswith("[FILE_READ_ERROR]"):
            # Remove error marker and return
            error_msg = file_data.replace("[FILE_READ_ERROR]", "")
            return False, error_msg
        
        # Create user input with file reference
        user_input = f"Reference: {file_path}. {user_prompt}"
        return True, (file_data, user_input)
