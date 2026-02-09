"""Help command handler."""


class HelpCommand:
    """Handler for help command to display available commands."""
    
    @staticmethod
    def show() -> None:
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
