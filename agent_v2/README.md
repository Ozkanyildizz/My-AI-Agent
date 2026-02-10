# ÖZKAN's AI Engineer Assistant V2

A powerful conversational AI assistant built with Groq API, featuring file analysis, conversation history management, and lesson logging capabilities.

## ✨ Features

- **🤖 Agentic Workflow**: Otonomous agent that can explore, read, and modify files without manual commands (NEW!)
- **📁 File Analysis**: Read and analyze code files with support for relative, absolute, and `~` paths
- **✍️ Code Extraction**: Extract code blocks from AI responses and save directly to files
- **🧠 Smart History Management**: Sliding window conversation history with automatic token optimization
- **📚 Lesson Learning**: Log and apply lessons from past interactions
- **🎯 Modular Architecture**: Clean command-based structure for easy maintenance
- **🔒 Secure Configuration**: Environment-based API key management  
- **📊 Comprehensive Logging**: Debug and track all operations
- **⚡ Robust Error Handling**: Custom exceptions and detailed error messages

## 🚀 Quick Start

### Agentic Mode (New!)
Just ask the agent to help you. It will autonomously use tools to explore your project.

```bash
# Example Prompts:
"Analyze the project structure and tell me what main.py does"
"Fix the bug in utils.py where it crashes on empty input"
"Create a new test file for the login module"
```

### Manual Mode (Legacy)
You can still use specific commands if you prefer total control.

```bash
read: main.py
write: test.py
```

### Prerequisites

- Python 3.8+
- Groq API key ([Get one here](https://console.groq.com))

### Installation

```bash
# Clone or navigate to project directory
cd my_ai_agent

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env
# Edit .env and add your GROQ_API_KEY
```

### Usage

```bash
# Start the AI assistant
python3 groq_chat.py
```

## 💡 Commands

### 1. `read:` - File Analysis
Analyze and explain code files.

**Syntax:**
```bash
read: <filepath> [prompt]
```

**Examples:**
```bash
read: main.py
read: ~/project/utils.py explain this
read: /absolute/path/test.py find bugs
```

**Supported Path Formats:**
- Relative: `test.py`, `../utils.py`
- Absolute: `/home/ozkan/project/main.py`
- Home directory: `~/my_project/app.py`

---

### 2. `write:` - Save Code Blocks
Extract code blocks from AI responses and save to files.

**Syntax:**
```bash
write: <filename>              # Single block or list if multiple
write: <index> <filename>      # Write specific block (1-based index)
write: list                    # Show all available blocks
write: all <filename>          # Write all blocks to one file
```

**Examples:**
```bash
# Ask AI for code, then:
write: test.py                 # Auto-write if 1 block found
write: 1 main.py               # Write the 1st code block
write: 2 utils.py              # Write the 2nd code block  
write: list                    # Preview all code blocks
write: all combined.txt        # Save all blocks in one file
```

**Use Case:**
No more copy-paste! Ask AI for code → `write: filename.py` → Done! ✨

---

### 3. `lesson:` - Log Lessons
Save important notes and learnings for future reference.

**Syntax:**
```bash
lesson: <text>
```

**Examples:**
```bash
lesson: Always validate user input
lesson: Use type hints for better code quality
```

Lessons are saved to `tasks/lessons.md` and automatically loaded on next session.

---

### 4. `help` - Show Commands
Display all available commands with examples.

```bash
help
```

---

### 5. `exit` / `quit` - Exit Application
Exit the application gracefully.

```bash
exit
quit
```

## 🏗️ Architecture

```
my_ai_agent/
├── groq_chat.py          # Main orchestrator (Agentic Loop)
├── config.py             # Configuration management
├── exceptions.py         # Custom exceptions
├── utils/                # Agent Utilities (NEW!)
│   ├── __init__.py
│   ├── tool_definitions.py # JSON Schemas for Tools
│   └── tool_handler.py     # Execution logic
├── commands/             # Legacy Command Handlers
│   ├── read_command.py
│   ├── write_command.py
│   ├── lesson_command.py
│   └── help_command.py
├── .env                  # Environment variables
├── requirements.txt      # Dependencies
└── tasks/
    └── lessons.md        # Logged lessons
```

### Key Components

#### Main Application
- **SeniorAIEngineer**: Intelligent Agent Class
  - `get_response()`: Manages the ReAct (Reason+Act) loop
  - `history`: Maintains conversation and tool outputs context

#### Agent Utilities (`utils/`)
- **ToolHandler**: Executes tool calls from the AI
- **tool_definitions**: Defines capabilities (Read, Write, List) provided to the LLM

#### Command Modules (Legacy Support)
- **ReadCommand**: Backward compatibility for `read:`
- **WriteCommand**: Backward compatibility for `write:`

#### Support Modules
- **Config**: Validated environment configuration
- **Exceptions**: Custom error types

**Code Reduction:** groq_chat.py went from 580 → 290 lines (50% reduction) through modularization!

## ⚙️ Configuration

```markdown
Environment variables in `.env`:

```bash
# Required
GROQ_API_KEY=your_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
ACTIVE_PROVIDER=gemini # for using gemini 

# Optional (with defaults)
GROQ_MODEL=llama-3.3-70b-versatile
GEMINI_MODEL=gemini-1.5-flash
MAX_HISTORY=20
HISTORY_KEEP=10
TEMPERATURE=0.2
TASKS_DIR=tasks
```
```


## 📝 Logging

All operations are logged to `ai_agent.log` file:

```
2026-02-09 21:18:45 - config - INFO - Configuration loaded: model=llama-3.3-70b-versatile
2026-02-09 21:18:45 - groq_chat - INFO - SeniorAIEngineer initialized successfully
```

## 🔒 Security

- ✅ API keys stored in `.env` (gitignored)
- ✅ Path validation for file operations
- ✅ UTF-8 encoding enforced
- ✅ Permission checks before file access

## 🐛 Troubleshooting

**"GROQ_API_KEY not found"**
- Ensure `.env` file exists with valid API key

**"File not found"**
- Check file path is correct
- Use absolute path or proper relative path

**"Rate limit reached"**
- Wait a moment and try again
- History automatically cleared for recovery

## 🤝 Contributing

This is a personal project by Özkan. Feedback and suggestions welcome!

## 📄 License

Personal project - All rights reserved

---

**Built by Özkan YILDIZ** 
