"""Tool definitions (JSON Schemas) for Groq API."""

tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read and analyze the content of a file. Use this when you need to understand code, find bugs, or review implementation details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string", 
                        "description": "Path to the file to read (e.g., 'main.py', 'src/utils.py')"
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create or overwrite a file with new content. Use this to fix bugs, add features, or create new modules.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path where the file should be created/updated"
                    },
                    "content": {
                        "type": "string",
                        "description": "The complete content to write to the file"
                    }
                },
                "required": ["file_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories in a specific path. Use this to explore the project structure or find specific files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to list (default: '.' for current directory)"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_instructions",
            "description": "Retrieve project instructions or lessons learned. Use this when you are unsure about project conventions or past decisions.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

def get_gemini_tools():
    """Convert OpenAI tools format to Gemini format."""
    gemini_tools = []
    for tool in tools:
        if "function" in tool:
             gemini_tools.append(tool["function"])
    return gemini_tools
