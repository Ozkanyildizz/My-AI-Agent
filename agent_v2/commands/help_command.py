"""Help command handler."""


class HelpCommand:
    """Handler for help command to display available commands."""
    
    @staticmethod
    def show() -> None:
        """Print available commands with examples."""
        print("\n\033[1;36m" + "="*60)
        print("AVAILABLE COMMANDS")
        print("="*60 + "\033[0m\n")
        
        print("\033[1;33m1. AGENTIC MODE (Autonomous)\033[0m")
        print("   \033[37mJust ask me to do anything! I can read, write, and list files.\033[0m")
        print("   \033[90mExamples:\033[0m")
        print("     Make a snake game.")
        print("     Fix the bug in main.py.")
        print("     Analyze this project structure.")
        print()
        
        print("\033[1;33m2. DUAL ENGINE (Provider Switching)\033[0m")
        print("   \033[37mSwitch between Groq (Speed) and Gemini (Reasoning)\033[0m")
        print("   \033[90mHow to Switch:\033[0m")
        print("     Edit \033[96m.env\033[0m file and set \033[96mACTIVE_PROVIDER=gemini\033[0m (or groq)")
        print()

        print("\033[1;33m3. MANUAL COMMANDS (Legacy)\033[0m")
        print("   \033[96mread: <file>\033[0m          Analyze a file manually")
        print("   \033[96write: <file>\033[0m          Save last code block to file")
        print("   \033[96mlesson: <text>\033[0m        Log a learned lesson")
        print()
        
        print("\033[1;33m4. help\033[0m")
        print("   \033[37mShow this help message\033[0m")
        print()
        
        print("\033[1;33m5. exit / quit\033[0m")
        print("   \033[37mExit the application\033[0m")
        print()
        
        print("\033[90m" + "-"*60 + "\033[0m")
        print("\033[95m💡 Tip:\033[0m Use 'Gemini' for complex reasonings and 'Groq' for fast coding!")
        print("\033[90m" + "-"*60 + "\033[0m\n")
