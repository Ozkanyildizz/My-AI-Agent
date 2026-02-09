"""
AI Engineer Chat Application

A conversational AI assistant using Groq API with file analysis capabilities,
conversation history management, and lesson logging.

Logging: All operations are logged to 'ai_agent.log' file.
"""

import os
import datetime
from typing import Optional, Tuple, List, Dict, Any
from groq import Groq

from config import Config
from exceptions import FileReadError, APIError, ConfigurationError
from write_helpers import extract_code_blocks, parse_write_command

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
    - Robust error handling and logging
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the AI Engineer assistant.
        
        Args:
            config: Optional Config object. Creates default if not provided.
        """
        self.config = config or Config()
        self.client = Groq(api_key=self.config.api_key)
        self.history: List[Dict[str, str]] = []
        self.last_response: str = ""  # Store last AI response for write command
        
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
                    f.write("# Lessons Learned Log\\n")
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
                    lessons_context = f"\\nRecent lessons learned from your history:\\n{last_lessons}"
        except FileNotFoundError:
            logger.warning("Lessons file not found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading lessons: {e}")

        self.history = [{
            "role": "system",
            "content": (
                "You are a Staff Software Engineer. "
                "Context: User is Ozkan, a Computer Engineering student (UAV/ROS2 AI ML Python C++ C# focus).\\n"
                f"{lessons_context}\\n"
                "Rules:\\n"
                "1. If a file is provided, analyze it line-by-line.\\n"
                "2. Follow 'Plan Mode': Architecture first, code second.\\n"
                "3. No Laziness: Find the root cause of bugs.\\n"
                "4. Minimal Impact: Suggest clean, focused changes."
            )
        }]
        logger.debug("System prompt loaded")

    def log_lesson(self, lesson_text: str) -> str:
        """
        Log a lesson learned for future reference.
        
        Args:
            lesson_text: The lesson to log
            
        Returns:
            Success message with file path
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            with open(self.config.lessons_file, "a", encoding="utf-8") as f:
                f.write(f"- [{timestamp}]: {lesson_text}\\n")
            logger.info(f"Logged lesson: {lesson_text[:50]}...")
            return f"Successfully logged to {self.config.lessons_file}"
        except Exception as e:
            logger.error(f"Failed to log lesson: {e}")
            return f"Error logging lesson: {str(e)}"

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

    def _parse_read_command(self, user_input: str) -> Optional[Tuple[str, str]]:
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

    def _process_file_read(self, file_path: str, user_prompt: str) -> Tuple[bool, str]:
        """
        Process file reading and add to conversation history.
        
        Args:
            file_path: Path to file to read
            user_prompt: User's analysis prompt
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        file_data = self.read_file_content(file_path)
        
        if file_data.startswith("[FILE_READ_ERROR]"):
            # Remove error marker and return
            error_msg = file_data.replace("[FILE_READ_ERROR]", "")
            return False, error_msg
        
        # Add file content to history
        file_msg = f"FILE CONTENT FOR ANALYSIS: {file_data}"
        self.history.append({"role": "user", "content": file_msg})
        
        # Create user input with file reference
        user_input = f"Reference: {file_path}. {user_prompt}"
        return True, user_input

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
            parse_result = self._parse_read_command(user_input)
            
            if parse_result:
                if parse_result[0]:  # Has file path
                    file_path, user_prompt = parse_result
                    file_was_read, user_input = self._process_file_read(file_path, user_prompt)
                    
                    if not file_was_read:  # Error occurred
                        return user_input  # user_input contains error message
                else:
                    return "\\033[91mError: No file path provided after 'read:' command\\033[0m"
            
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

    def handle_write_command(self, user_input: str) -> str:
        """
        Handle write: command to extract and save code blocks.
        
        Args:
            user_input: User's write command
            
        Returns:
            Status message
        """
        # Check if we have a last response
        if not self.last_response:
            return "\033[91mNo previous AI response to extract code from.\033[0m"
        
        # Parse command
        parsed = parse_write_command(user_input)
        if not parsed:
            return ("\033[91mInvalid write command format.\033[0m\n"
                   "Usage: write: filename.py, write: 1 filename.py, "
                   "write: list, write: all filename.py")
        
        action, filename, index = parsed
        
        # Extract code blocks
        blocks = extract_code_blocks(self.last_response)
        
        if not blocks:
            return "\033[91mNo code blocks found in last response.\033[0m"
        
        logger.info(f"Write command: action={action}, filename={filename}, index={index}, blocks={len(blocks)}")
        
        # Handle list action
        if action == 'list':
            return self._list_code_blocks(blocks)
        
        # Handle all action
        if action == 'all':
            return self._write_all_blocks(blocks, filename)
        
        # Handle write action
        if index is not None:
            # Write specific block
            if index < 1 or index > len(blocks):
                return (f"\033[91mInvalid index {index}. "
                       f"Available blocks: 1-{len(blocks)}\033[0m")
            return self._write_single_block(blocks[index - 1], filename, index, len(blocks))
        else:
            # No index specified
            if len(blocks) == 1:
                # Auto-write single block
                return self._write_single_block(blocks[0], filename, 1, 1)
            else:
                # Multiple blocks, show list
                return (f"\033[93m⚠️  Found {len(blocks)} code blocks. "
                       f"Specify which one:\033[0m\n" + 
                       self._list_code_blocks(blocks) +
                       f"\n\033[90mUse: write: 1 {filename}\033[0m")
    
    def _list_code_blocks(self, blocks: List[Dict[str, str]]) -> str:
        """Format code blocks list for display."""
        output = ["\n\033[1;36m📋 Code blocks in last response:\033[0m\n"]
        
        for i, block in enumerate(blocks, 1):
            lang = block['language']
            code = block['code']
            lines = code.split('\n')
            line_count = len(lines)
            
            output.append(f"\033[1;33m{i}. [{lang}]\033[0m {line_count} line{'s' if line_count > 1 else ''}")
            output.append("\033[90m" + "─" * 40 + "\033[0m")
            
            # Show preview (first 3 lines)
            preview_lines = lines[:3]
            for line in preview_lines:
                output.append(f"   {line}")
            
            if line_count > 3:
                output.append(f"   \033[90m... ({line_count - 3} more lines)\033[0m")
            output.append("")
        
        return "\n".join(output)
    
    def _write_single_block(self, block: Dict[str, str], filename: str, 
                           index: int, total: int) -> str:
        """Write a single code block to file."""
        try:
            code = block['code']
            lang = block['language']
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(code)
                if not code.endswith('\n'):
                    f.write('\n')
            
            line_count = len(code.split('\n'))
            logger.info(f"Wrote code block {index}/{total} to {filename} ({line_count} lines, {lang})")
            
            return (f"\033[92m✅ Code block {index}/{total} written to {filename}\033[0m\n"
                   f"   \033[90m({line_count} lines, {lang})\033[0m")
        
        except PermissionError:
            return f"\033[91mError: Permission denied to write file: {filename}\033[0m"
        except Exception as e:
            logger.error(f"Error writing file {filename}: {e}")
            return f"\033[91mError writing file: {str(e)}\033[0m"
    
    def _write_all_blocks(self, blocks: List[Dict[str, str]], filename: str) -> str:
        """Write all code blocks to a single file with separators."""
        try:
            total_lines = 0
            with open(filename, 'w', encoding='utf-8') as f:
                for i, block in enumerate(blocks, 1):
                    lang = block['language']
                    code = block['code']
                    
                    # Write separator
                    f.write(f"# ===== Code Block {i}/{len(blocks)} [{lang}] =====\n\n")
                    f.write(code)
                    if not code.endswith('\n'):
                        f.write('\n')
                    f.write('\n')
                    
                    total_lines += len(code.split('\n'))
            
            logger.info(f"Wrote {len(blocks)} code blocks to {filename} ({total_lines} total lines)")
            
            return (f"\033[92m✅ {len(blocks)} code blocks written to {filename}\033[0m\n"
                   f"   \033[90m({total_lines} total lines)\033[0m")
        
        except PermissionError:
            return f"\033[91mError: Permission denied to write file: {filename}\033[0m"
        except Exception as e:
            logger.error(f"Error writing file {filename}: {e}")
            return f"\033[91mError writing file: {str(e)}\033[0m"


def print_help() -> None:
    """Print available commands with examples."""
    print("\n\033[1;36m" + "="*60)
    print("📚 AVAILABLE COMMANDS")
    print("="*60 + "\033[0m\n")
    
    print("\033[1;33m1. read:\033[0m \033[90m<file_path>\033[0m \033[90m[prompt]\033[0m")
    print("   \033[37mAnalyze and explain code files\033[0m")
    print("   \033[90mExamples:\033[0m")
    print("     \033[96mread: main.py\033[0m")
    print("     \033[96mread: ~/project/test.py explain this code\033[0m")
    print("     \033[96mread: /absolute/path/script.py find bugs\033[0m")
    print()
    
    print("\033[1;33m2. lesson:\033[0m \033[90m<text>\033[0m")
    print("   \033[37mLog important lessons to lessons.md\033[0m")
    print("   \033[90mExamples:\033[0m")
    print("     \033[96mlesson: Always validate user input\033[0m")
    print("     \033[96mlesson: Use type hints for better code quality\033[0m")
    print()
    
    print("\033[1;33m3. write:\033[0m \033[90m[index]\033[0m \033[90m<filename>\033[0m")
    print("   \033[37mExtract and save code blocks from last AI response\033[0m")
    print("   \033[90mExamples:\033[0m")
    print("     \033[96mwrite: test.py\033[0m              \033[90m# Single block or list\033[0m")
    print("     \033[96mwrite: 1 main.py\033[0m            \033[90m# Write block #1\033[0m")
    print("     \033[96mwrite: list\033[0m                 \033[90m# Show all blocks\033[0m")
    print("     \033[96mwrite: all output.txt\033[0m       \033[90m# All blocks to file\033[0m")
    print()
    
    print("\033[1;33m4. help\033[0m")
    print("   \033[37mShow this help message\033[0m")
    print()
    
    print("\033[1;33m5. exit / quit\033[0m")
    print("   \033[37mExit the application\033[0m")
    print()
    
    print("\033[90m" + "-"*60 + "\033[0m")
    print("\033[95m💡 Tip:\033[0m All previous conversations are remembered!")
    print("\033[90m" + "-"*60 + "\033[0m\n")


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
                    print_help()
                    continue
                
                if user_msg.lower().startswith("lesson:"):
                    text = user_msg.split("lesson:", 1)[1].strip()
                    result = engineer.log_lesson(text)
                    print(f"\033[93m>> {result}\033[0m")
                    continue
                
                if user_msg.lower().startswith("write:"):
                    result = engineer.handle_write_command(user_msg)
                    print(result)
                    continue
                
                response = engineer.get_response(user_msg)
                engineer.last_response = response  # Store for write command
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
