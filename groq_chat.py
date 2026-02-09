"""
AI Engineer Chat Application

A conversational AI assistant using Groq API with file analysis capabilities,
conversation history management, and lesson logging.

Logging: All operations are logged to 'ai_agent.log' file.
"""

import os
from typing import List, Dict, Any
from groq import Groq

from config import Config
from exceptions import APIError, ConfigurationError
from commands import ReadCommand, WriteCommand, LessonCommand, HelpCommand

# Note: Logging is configured in config.py to write to ai_agent.log
import logging
logger = logging.getLogger(__name__)


class SeniorAIEngineer:
    """
    AI-powered software engineering assistant.
    
    Features:
    - File reading and analysis with multiple path formats
    - Conversation history management with sliding window
    - Lesson logging and learning from past interactions
    - Code block extraction and file writing
    - Robust error handling and logging
    """
    
    def __init__(self, config: Config = None):
        """
        Initialize the AI Engineer assistant.
        
        Args:
            config: Optional Config object. Creates default if not provided.
        """
        self.config = config or Config()
        self.client = Groq(api_key=self.config.api_key)
        self.history: List[Dict[str, str]] = []
        
        # Initialize command handlers
        self.read_cmd = ReadCommand(self.config)
        self.write_cmd = WriteCommand(self.config)
        self.lesson_cmd = LessonCommand(self.config)
        self.help_cmd = HelpCommand()
        
        self._init_workspace()
        self._load_system_prompt()
        logger.info("SeniorAIEngineer initialized successfully")

    def _init_workspace(self) -> None:
        """Initialize workspace directories and files."""
        try:
            if not os.path.exists(self.config.tasks_dir):
                os.makedirs(self.config.tasks_dir)
                logger.info(f"Created tasks directory: {self.config.tasks_dir}")
            
            if not os.path.exists(self.config.lessons_file):
                with open(self.config.lessons_file, "w", encoding="utf-8") as f:
                    f.write("# Lessons Learned Log\n")
                logger.info(f"Created lessons file: {self.config.lessons_file}")
        except OSError as e:
            logger.error(f"Failed to initialize workspace: {e}")
            raise ConfigurationError(f"Failed to initialize workspace: {e}")

    def _load_system_prompt(self) -> None:
        """Load system prompt with recent lessons context."""
        lessons_context = ""
        try:
            with open(self.config.lessons_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if len(lines) > 1:  # More than just the header
                    last_lessons = "".join(lines[-5:])
                    lessons_context = f"\nRecent lessons learned from your history:\n{last_lessons}"
        except FileNotFoundError:
            logger.warning("Lessons file not found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading lessons: {e}")

        self.history = [{
            "role": "system",
            "content": (
                "You are a Staff Software Engineer. "
                "Context: User is Ozkan, a Computer Engineering student (UAV/ROS2 AI ML Python C++ C# focus).\n"
                f"{lessons_context}\n"
                "Rules:\n"
                "1. If a file is provided, analyze it line-by-line.\n"
                "2. Follow 'Plan Mode': Architecture first, code second.\n"
                "3. No Laziness: Find the root cause of bugs.\n"
                "4. Minimal Impact: Suggest clean, focused changes."
            )
        }]
        logger.debug("System prompt loaded")

    def _manage_history(self, file_was_read: bool) -> None:
        """
        Manage conversation history with sliding window.
        
        Args:
            file_was_read: Whether a file was read in this interaction
        """
        # Sliding window for memory management
        if len(self.history) > self.config.max_history:
            self.history = [self.history[0]] + self.history[-self.config.history_keep:]
            logger.debug(f"Trimmed history to {len(self.history)} messages")
        
        # Remove file content from history after response (token saving)
        if file_was_read and len(self.history) >= 3:
            # Remove the file content message (3rd from end)
            self.history.pop(-3)
            logger.debug("Removed file content from history for token efficiency")

    def _call_ai_api(self, user_input: str) -> str:
        """
        Make API call to Groq and get response.
        
        Args:
            user_input: User's message
            
        Returns:
            AI response
            
        Raises:
            APIError: If API call fails
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.config.model,
                messages=self.history,
                temperature=self.config.temperature
            )
            response = completion.choices[0].message.content
            logger.info(f"Received AI response ({len(response)} chars)")
            return response
            
        except Exception as e:
            error_str = str(e).lower()
            
            if "length" in error_str or "rate_limit" in error_str:
                logger.error(f"API limit reached: {e}")
                # Clear history except system prompt
                self.history = [self.history[0]]
                raise APIError(
                    "System limit reached. Memory cleared for safety. Please try again.",
                    error_type="rate_limit"
                )
            
            logger.error(f"API call failed: {e}")
            raise APIError(f"API execution error: {str(e)}")

    def get_response(self, user_input: str) -> str:
        """
        Main method to get AI response for user input.
        
        Handles file reading commands, conversation history, and API calls.
        
        Args:
            user_input: User's input message
            
        Returns:
            AI response or error message
        """
        file_was_read = False
        
        try:
            # Check for read: command
            parse_result = self.read_cmd.parse_command(user_input)
            
            if parse_result:
                file_path, user_prompt = parse_result
                success, result = self.read_cmd.process(file_path, user_prompt)
                
                if not success:  # Error occurred
                    return result  # result contains error message
                
                # Unpack file data and formatted user input
                file_data, user_input = result
                
                # Add file content to history
                file_msg = f"FILE CONTENT FOR ANALYSIS: {file_data}"
                self.history.append({"role": "user", "content": file_msg})
                file_was_read = True
            
            # Add user message to history
            self.history.append({"role": "user", "content": user_input})
            
            # Get AI response
            response = self._call_ai_api(user_input)
            
            # Add assistant response to history
            self.history.append({"role": "assistant", "content": response})
            
            # Manage history (sliding window and file content removal)
            self._manage_history(file_was_read)
            
            return response
            
        except APIError as e:
            return str(e)
        except Exception as e:
            logger.error(f"Unexpected error in get_response: {e}", exc_info=True)
            return f"\033[91mUnexpected error: {str(e)}\033[0m"


def main() -> None:
    """Main entry point for the application."""
    try:
        config = Config()
        engineer = SeniorAIEngineer(config)
        
        # Display header
        print("\033[94m" + "="*50)
        print("ÖZKAN'S AGENT ACTIVE")
        print("="*50 + "\033[0m")
        print("\033[93m📊 Current Model:\033[0m", config.model)
        print("\033[95mPRO-TIPS & COMMANDS:\033[0m")
        print("  • \033[96mread:\033[0m <file.py> [prompt]  -> Analyze local code")
        print("    \033[90m(Supports: relative paths, absolute paths, ~/home paths)\033[0m")
        print("  • \033[96mwrite:\033[0m [index] <file>     -> Save code from AI response")
        print("  • \033[96mlesson:\033[0m <text>            -> Log patterns to lessons.md")
        print("  • \033[96mhelp\033[0m                      -> Show all commands")
        print("  • \033[96mexit/quit\033[0m                 -> Terminate session")
        print("\033[94m" + "-"*50 + "\033[0m")
        
        # Display recent memory
        print("\033[93m[Memory Check] Recent Lessons Applied:\033[0m")
        try:
            with open(config.lessons_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if len(lines) > 1:
                    print("".join(lines[-3:]))
                else:
                    print("No lessons found yet.")
        except FileNotFoundError:
            print("No lessons found yet.")
        
        # Main loop
        while True:
            try:
                user_msg = input("\n\033[1;32m[User]:\033[0m ")  # Bright green
                
                if user_msg.lower() in ["exit", "quit"]:
                    logger.info("User exited application")
                    break
                
                if user_msg.lower().strip() == "help":
                    engineer.help_cmd.show()
                    continue
                
                if user_msg.lower().startswith("lesson:"):
                    text = user_msg.split("lesson:", 1)[1].strip()
                    result = engineer.lesson_cmd.log(text)
                    print(f"\033[93m>> {result}\033[0m")
                    continue
                
                if user_msg.lower().startswith("write:"):
                    result = engineer.write_cmd.handle(user_msg)
                    print(result)
                    continue
                
                response = engineer.get_response(user_msg)
                engineer.write_cmd.set_last_response(response)  # Store for write command
                print(f"\n\033[1;34m[Agent]:\033[0m\n{response}")  # Bright blue
                
            except KeyboardInterrupt:
                print("\n\033[93mInterrupted by user. Use 'exit' to quit.\033[0m")
                continue
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                print(f"\033[91mError: {str(e)}\033[0m")
    
    except ConfigurationError as e:
        print(f"\033[91m{str(e)}\033[0m")
        print("Please check your .env file and try again.")
        exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\033[91mFatal error: {str(e)}\033[0m")
        exit(1)


if __name__ == "__main__":
    main()
