"""Tool execution handler."""

import os
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class ToolHandler:
    """Handles execution of tools requested by the AI."""
    
    def __init__(self, engineer):
        """
        Initialize tool handler.
        
        Args:
            engineer: The SeniorAIEngineer instance to access commands
        """
        self.engineer = engineer
    
    def handle_tool_calls(self, tool_calls: List[Any]) -> List[Dict[str, Any]]:
        """
        Execute a list of tool calls and return results.
        
        Args:
            tool_calls: List of tool call objects from Groq API
            
        Returns:
            List of tool output messages for the chat history
        """
        results = []
        
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            call_id = tool_call.id
            
            logger.info(f"Executing tool: {function_name} with args: {function_args}")
            
            try:
                result_content = self._execute(function_name, function_args)
            except Exception as e:
                logger.error(f"Error executing {function_name}: {e}")
                result_content = f"Error executing tool: {str(e)}"
            
            # Format result for Groq API
            results.append({
                "role": "tool",
                "tool_call_id": call_id,
                "name": function_name,
                "content": str(result_content)
            })
            
        return results
    
    def _execute(self, name: str, args: Dict[str, Any]) -> str:
        """Execute a single tool."""
        if name == "read_file":
            return self.engineer.read_cmd.read_file_content(args["file_path"])
            
        elif name == "write_file":
            # Direct writing without extraction logic (since AI provides full content)
            path = args["file_path"]
            content = args["content"]
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Tool wrote file: {path}")
                return f"Successfully wrote to {path}"
            except Exception as e:
                return f"Failed to write file: {e}"
                
        elif name == "list_files":
            path = args.get("path", ".")
            try:
                files = os.listdir(path)
                # Filter out hidden files and __pycache__
                files = [f for f in files if not f.startswith('.') and f != '__pycache__']
                return f"Files in {path}:\n" + "\n".join(files)
            except Exception as e:
                return f"Error listing files: {e}"
                
        elif name == "get_instructions":
            # Return content of lessons.md
            try:
                with open(self.engineer.config.lessons_file, "r", encoding="utf-8") as f:
                    return f.read()
            except FileNotFoundError:
                return "No lessons recorded yet."
        
        return f"Unknown tool: {name}"
