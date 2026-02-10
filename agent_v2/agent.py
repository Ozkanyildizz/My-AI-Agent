"""
AI Engineer Chat Application

A conversational AI assistant using Groq and Gemini APIs with file analysis capabilities,
conversation history management, and lesson logging.

Features:
- Dual Engine: Switch between Groq (Speed) and Gemini (Reasoning)
- Agentic Workflow: Autonomous tool usage (read, write, list files)
- Manual Commands: read:, write:, lesson: (Backward compatibility)
- Smart History: Sliding window context management
- Persistent Logging: Operations logged to ai_agent.log
"""

import os
import json
from typing import List, Dict, Any, Union
import logging

from groq import Groq
from groq.types.chat import ChatCompletionMessage
from google import genai
from google.genai import types

from config import Config
from exceptions import APIError, ConfigurationError
from commands import ReadCommand, WriteCommand, LessonCommand, HelpCommand
from utils import tools, ToolHandler 
from utils.tool_definitions import get_gemini_tools
logger = logging.getLogger(__name__)


class AIClient:
    """Wrapper for handling multiple AI providers (Groq, Gemini)."""
    
    def __init__(self, config: Config):
        self.config = config
        self.provider = config.active_provider
        
        # Initialize Groq
        if config.api_key:
            self.groq_client = Groq(api_key=config.api_key)
            
        # Initialize Gemini (New SDK)
        if config.gemini_api_key:
            self.gemini_client = genai.Client(api_key=config.gemini_api_key)

    def generate_response(self, messages: List[Dict], tools_def: List[Dict] = None) -> Union[str, Any]:
        """
        Generate response using the active provider.
        Returns either a string content or a message object with tool calls.
        """
        if self.provider == "gemini":
            return self._generate_gemini(messages, tools_def)
        else:
            return self._generate_groq(messages, tools_def)

    def _generate_groq(self, messages, tools_def):
        """Handle Groq API call."""
        completion = self.groq_client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            tools=tools_def,
            tool_choice="auto" if tools_def else None,
            temperature=self.config.temperature
        )
        return completion.choices[0].message

    def _generate_gemini(self, messages, tools_def):
        """Handle Gemini API call with Tool Support."""
        # Convert OpenAI-format messages to Gemini format
        gemini_contents = []
        system_instruction = ""
        
        for msg in messages:
            # Handle both dict and object types
            if isinstance(msg, dict):
                role = msg.get("role")
                content = msg.get("content", "")
                tool_calls = msg.get("tool_calls")
                tool_call_id = msg.get("tool_call_id")
                name = msg.get("name") # For tool output
            else:
                role = getattr(msg, "role", "assistant")
                content = getattr(msg, "content", "") or ""
                tool_calls = getattr(msg, "tool_calls", None)
                tool_call_id = getattr(msg, "tool_call_id", None)
                name = getattr(msg, "name", None)

            # Gemini requires non-empty content
            if not content and not tool_calls and not tool_call_id and role != "system":
                 continue

            if role == "system":
                system_instruction = content
            elif role == "user":
                gemini_contents.append(types.Content(role="user", parts=[types.Part.from_text(text=content)]))
            elif role == "assistant":
                parts = []
                if content:
                    parts.append(types.Part.from_text(text=content))
                
                if tool_calls:
                     # Add Function Call to history
                     for tc in tool_calls:
                         # Let SDK handle thought_signature automatically
                         fc_part = types.Part.from_function_call(
                             name=tc.function.name, 
                             args=json.loads(tc.function.arguments)
                         )
                         parts.append(fc_part)
                
                if parts:
                    gemini_contents.append(types.Content(role="model", parts=parts))
            elif role == "tool":
                # Add Function Response to history
                gemini_contents.append(types.Content(role="tool", parts=[types.Part.from_function_response(name=name, response={"result": content})]))

        try:
            # Configure generation
            gemini_tool_config = []
            if tools_def:
                funcs = []
                for t in tools_def:
                    if "function" in t:
                        f = t["function"]
                        funcs.append(types.FunctionDeclaration(
                            name=f["name"],
                            description=f["description"],
                            parameters=f["parameters"]
                        ))
                if funcs:
                    gemini_tool_config = [types.Tool(function_declarations=funcs)]

            config = types.GenerateContentConfig(
                temperature=self.config.temperature,
                system_instruction=system_instruction,
                tools=gemini_tool_config
            )
            
            # Use models/gemini-2.5-flash (verified available in API)
            response = self.gemini_client.models.generate_content(
                model='models/gemini-2.5-flash',
                contents=gemini_contents,
                config=config
            )
            
            # Parse response
            # Check for function calls
            tool_calls = []
            final_content = ""
            
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.text:
                        final_content += part.text
                    if part.function_call:
                        # Convert to OpenAI ToolCall format
                        tc_dict = {
                            "id": "call_" + part.function_call.name,
                            "type": "function",
                            "function": {
                                "name": part.function_call.name,
                                "arguments": json.dumps(part.function_call.args)
                            }
                        }
                        tool_calls.append(tc_dict)

            # Mock a message object (like Groq's)
            class MockMessage:
                def __init__(self, content, tool_calls_list=None):
                    self.content = content
                    self.tool_calls = None
                    if tool_calls_list:
                         class ToolCallObj:
                             def __init__(self, tc_dict):
                                 self.id = tc_dict["id"]
                                 self.type = tc_dict["type"]
                                 self.function = self.FunctionObj(tc_dict["function"])
                             
                             class FunctionObj:
                                 def __init__(self, func_dict):
                                     self.name = func_dict["name"]
                                     self.arguments = func_dict["arguments"]
                         
                         self.tool_calls = [ToolCallObj(tc) for tc in tool_calls_list]

            return MockMessage(final_content, tool_calls)

        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            raise APIError(f"Gemini Error: {e}")



class SeniorAIEngineer:
    """
    AI-powered software engineering assistant with Agentic capabilities.
    """
    
    def __init__(self, config: Config = None):
        """Initialize the AI Engineer assistant."""
        self.config = config or Config()
        self.client = AIClient(self.config)
        self.history: List[Dict[str, Any]] = []
        
        # Initialize command handlers
        self.read_cmd = ReadCommand(self.config)
        self.write_cmd = WriteCommand(self.config)
        self.lesson_cmd = LessonCommand(self.config)
        self.help_cmd = HelpCommand()
        
        # Initialize Agentic Tool Handler
        self.tool_handler = ToolHandler(self)
        
        self._init_workspace()
        self._load_system_prompt()
        logger.info(f"SeniorAIEngineer initialized (Provider: {self.config.active_provider})")

    def _init_workspace(self) -> None:
        """Initialize workspace directories and files."""
        try:
            if not os.path.exists(self.config.tasks_dir):
                os.makedirs(self.config.tasks_dir)
            
            if not os.path.exists(self.config.lessons_file):
                with open(self.config.lessons_file, "w", encoding="utf-8") as f:
                    f.write("# Lessons Learned Log\n")
        except OSError as e:
            logger.error(f"Failed to initialize workspace: {e}")
            raise ConfigurationError(f"Failed to initialize workspace: {e}")

    def _load_system_prompt(self) -> None:
        """Load system prompt with tool instructions."""
        lessons_context = ""
        try:
            with open(self.config.lessons_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if len(lines) > 1:
                    last_lessons = "".join(lines[-5:])
                    lessons_context = f"\nRecent lessons learned:\n{last_lessons}"
        except FileNotFoundError:
            pass

        self.history = [{
            "role": "system",
            "content": (
                "You are a Senior AI Software Engineer acting as an autonomous agent.\n"
                f"Context: User is Özkan, a Computer Engineering student (Robots and AI-ML focus).\n"
                f"{lessons_context}\n\n"
                "Refined Capabilities:\n"
                "1. **Agentic Workflow**: You have access to tools (`read_file`, `write_file`, `list_files`, `get_instructions`).\n"
                "2. **Proactive Solving**: When asked to solve a problem, USE TOOLS immediately.\n"
                "3. **MANDATORY RULE**: NEVER just print code in the chat if asked to create/fix a file. ALWAYS use `write_file` tool.\n"
                "   - BAD: 'Here is the code: ```python ...```'\n"
                "   - GOOD: Call `write_file(path='...', content='...')`\n"
                "4. **Plan & Execute**: Investigate -> Plan -> Execute (Write).\n"
                "5. **Dual Engine**: You are powered by Groq or Gemini. Both have full tool access.\n"
                "6. **Phantom Tools**: Do NOT try to call tools that don't exist (like 'exit').\n"
            )
        }]
        logger.debug("System prompt loaded with agentic instructions")

    def _manage_history(self) -> None:
        """Manage conversation history with sliding window."""
        if len(self.history) > self.config.max_history:
            # Keep system prompt + last N messages
            self.history = [self.history[0]] + self.history[-self.config.history_keep:]
            logger.debug(f"Trimmed history to {len(self.history)} messages")

    def get_response(self, user_input: str) -> str:
        """
        Main Agentic Loop: User Input -> [Tool Loop] -> Final Response.
        """
        try:
            # 1. Handle Legacy Manual Commands
            if user_input.lower().startswith("read:"):
                parse_result = self.read_cmd.parse_command(user_input)
                if parse_result:
                    file_path, user_prompt = parse_result
                    success, result = self.read_cmd.process(file_path, user_prompt)
                    if not success: return result
                    file_data, prompt = result
                    self.history.append({"role": "user", "content": f"FILE: {file_data}\nPROMPT: {prompt}"})
                    
            elif user_input.lower().startswith("write:"):
                return self.write_cmd.handle(user_input)
            else:
                self.history.append({"role": "user", "content": user_input})

            # 2. Agentic Loop
            loop_count = 0
            MAX_LOOPS = 15
            
            while loop_count < MAX_LOOPS:
                loop_count += 1
                
                # Use AIClient wrapper to generate response
                # ALWAYS pass tools now, as both providers support it
                tools_to_use = tools
                
                message = self.client.generate_response(self.history, tools_to_use)
                
                # If it's a real message object (Groq-style) and has content
                if hasattr(message, 'content') and message.content:
                    # If this was a terminal response (no tools)
                    if not getattr(message, 'tool_calls', None):
                         self.history.append({"role": "assistant", "content": message.content}) # Convert to dict
                         self._manage_history()
                         return message.content
                
                # If it has tool calls (Groq only for now)
                if getattr(message, 'tool_calls', None):
                    self.history.append(message) # Add tool call to history
                    logger.info(f"AI requested {len(message.tool_calls)} tool calls")
                    tool_outputs = self.tool_handler.handle_tool_calls(message.tool_calls)
                    self.history.extend(tool_outputs)
                    continue # Loop again
                
                # Fallback for simple content return (Gemini)
                if hasattr(message, 'content'):
                     self.history.append({"role": "assistant", "content": message.content})
                     return message.content

            return "Loop limit reached."

        except Exception as e:
            logger.error(f"Error in agentic loop: {e}", exc_info=True)
            return f"\033[91mSystem Error: {str(e)}\033[0m"


def main() -> None:
    """Main entry point."""
    try:
        config = Config()
        engineer = SeniorAIEngineer(config)
        
        # Display header
        print("\033[94m" + "="*60)
        print("ÖZKAN'S AI AGENT (Dual Engine)")
        print("="*60 + "\033[0m")
        print(f"\033[93m Active Provider:\033[0m {config.active_provider.upper()}")
        if config.active_provider == "groq":
             print(f"\033[90m   Model: {config.model}\033[0m")
        else:
             print(f"\033[90m   Model: gemini-2.5-flash\033[0m")
             
        print("\033[95m🤖 CAPABILITIES:\033[0m")
        print("  • \033[96mAgentic Mode:\033[0m Autonomous tool usage")
        print("  • \033[96mReasoning Mode:\033[0m Complex analysis (Gemini)")
        print("  • \033[96mManual Override:\033[0m 'read:', 'write:', 'lesson:', 'help'")
        print("\033[94m" + "-"*60 + "\033[0m")
        
        # Main loop
        while True:
            try:
                user_msg = input("\n\033[1;32m[User]:\033[0m ")
                
                if user_msg.lower() in ["exit", "quit"]:
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

                # Agentic Execution
                response = engineer.get_response(user_msg)
                
                engineer.write_cmd.set_last_response(response) 
                print(f"\n\033[1;34m[Agent]:\033[0m\n{response}")
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"\033[91mError: {str(e)}\033[0m")
    
    except Exception as e:
        print(f"Fatal Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
