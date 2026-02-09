# ÖZKAN's AI Engineer Assistant

A powerful conversational AI assistant built with Groq API, featuring file analysis, conversation history management, and lesson logging capabilities.

## ✨ Features

- **📁 File Analysis**: Read and analyze code files with support for relative, absolute, and `~` paths
- **🧠 Smart History Management**: Sliding window conversation history with automatic token optimization
- **📚 Lesson Learning**: Log and apply lessons from past interactions
- **🔒 Secure Configuration**: Environment-based API key management  
- **📊 Comprehensive Logging**: Debug and track all operations
- **⚡ Robust Error Handling**: Custom exceptions and detailed error messages

## 🚀 Quick Start

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

| Command | Description | Example |
|---------|-------------|---------|
| `read: <file>` | Analyze a code file | `read: main.py explain this code` |
| `lesson: <text>` | Log a lesson | `lesson: Always validate user input` |
| `exit` or `quit` | Exit the application | `exit` |

### File Reading Examples

```bash
# Relative path
read: test.py

# Absolute path  
read: /home/user/project/main.py what does this do?

# Home directory
read: ~/my_project/app.py analyze the architecture

# With custom prompt
read: utils.py find potential bugs
```

## 🏗️ Architecture

```
my_ai_agent/
├── groq_chat.py        # Main application (refactored)
├── config.py           # Configuration management
├── exceptions.py       # Custom exceptions
├── .env                # Environment variables (not in git)
├── requirements.txt    # Dependencies
└── tasks/
    └── lessons.md      # Logged lessons
```

### Key Components

- **SeniorAIEngineer**: Main AI assistant class
  - `_parse_read_command()`: Parse file read commands
  - `_process_file_read()`: Handle file reading
  - `_manage_history()`: Manage conversation history
  - `_call_ai_api()`: Make API calls to Groq
- **Config**: Validated configuration management
- **Custom Exceptions**: Specific error types for better handling

## ⚙️ Configuration

Environment variables in `.env`:

```bash
# Required
GROQ_API_KEY=your_api_key_here

# Optional (with defaults)
GROQ_MODEL=llama-3.3-70b-versatile
MAX_HISTORY=20
HISTORY_KEEP=10
TEMPERATURE=0.2
TASKS_DIR=tasks
```

## 🧪 Testing

```bash
# Run verification tests
python3 test_refactoring.py
```

## 📝 Logging

Logs are outputted to console with timestamps:

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

## 📚 Recent Updates (Phase 1)

✅ **Modularization**: Broke down monolithic `get_response()` into 4 focused methods  
✅ **Type Hints**: Full type annotations for better IDE support  
✅ **Error Handling**: Custom exception classes with detailed messages  
✅ **Logging**: Comprehensive logging system  
✅ **Configuration**: Validated config class with environment variables  
✅ **Documentation**: Complete docstrings and this README

## 🤝 Contributing

This is a personal project by Özkan. Feedback and suggestions welcome!

## 📄 License

Personal project - All rights reserved

---

**Built by Özkan** | **Powered by** [Groq](https://groq.com)
