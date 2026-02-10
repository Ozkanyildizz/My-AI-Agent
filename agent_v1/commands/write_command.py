"""Code block extraction and writing command handler."""

import re
import logging
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class WriteCommand:
    """Handler for write: command to extract and save code blocks."""
    
    def __init__(self, config):
        """Initialize write command handler.
        
        Args:
            config: Application configuration object
        """
        self.config = config
        self.last_response = ""
    
    def set_last_response(self, response: str) -> None:
        """
        Store last AI response for code extraction.
        
        Args:
            response: The last AI response text
        """
        self.last_response = response
    
    def extract_code_blocks(self, text: str) -> List[Dict[str, str]]:
        """
        Extract code blocks from markdown-formatted text.
        
        Args:
            text: Markdown text containing code blocks
            
        Returns:
            List of dicts with 'language' and 'code' keys
        """
        # Match ```language\ncode\n``` pattern
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        blocks = []
        for lang, code in matches:
            blocks.append({
                'language': lang.strip() if lang else 'text',
                'code': code.strip()
            })
        
        return blocks
    
    def parse_command(self, command: str) -> Optional[Tuple[str, str, Optional[int]]]:
        """
        Parse write: command into components.
        
        Args:
            command: User input starting with "write:"
            
        Returns:
            (action, filename, index) tuple or None
            - action: 'write', 'list', or 'all'
            - filename: target filename (or empty for 'list')
            - index: 1-based index or None
        """
        # Remove "write:" prefix and strip
        parts = command.lower().replace("write:", "").strip().split()
        
        if not parts:
            return None
        
        # write: list
        if parts[0] == "list":
            return ('list', '', None)
        
        # write: all filename
        if parts[0] == "all":
            if len(parts) < 2:
                return None
            return ('all', parts[1], None)
        
        # write: filename or write: index filename
        if len(parts) == 1:
            # write: filename.py
            return ('write', parts[0], None)
        
        # write: 1 filename.py
        try:
            index = int(parts[0])
            filename = parts[1]
            return ('write', filename, index)
        except (ValueError, IndexError):
            return None
    
    def handle(self, user_input: str) -> str:
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
        parsed = self.parse_command(user_input)
        if not parsed:
            return ("\033[91mInvalid write command format.\033[0m\n"
                   "Usage: write: filename.py, write: 1 filename.py, "
                   "write: list, write: all filename.py")
        
        action, filename, index = parsed
        
        # Extract code blocks
        blocks = self.extract_code_blocks(self.last_response)
        
        if not blocks:
            return "\033[91mNo code blocks found in last response.\033[0m"
        
        logger.info(f"Write command: action={action}, filename={filename}, index={index}, blocks={len(blocks)}")
        
        # Handle list action
        if action == 'list':
            return self._list_blocks(blocks)
        
        # Handle all action
        if action == 'all':
            return self._write_all(blocks, filename)
        
        # Handle write action
        if index is not None:
            # Write specific block
            if index < 1 or index > len(blocks):
                return (f"\033[91mInvalid index {index}. "
                       f"Available blocks: 1-{len(blocks)}\033[0m")
            return self._write_single(blocks[index - 1], filename, index, len(blocks))
        else:
            # No index specified
            if len(blocks) == 1:
                # Auto-write single block
                return self._write_single(blocks[0], filename, 1, 1)
            else:
                # Multiple blocks, show list
                return (f"\033[93m⚠️  Found {len(blocks)} code blocks. "
                       f"Specify which one:\033[0m\n" + 
                       self._list_blocks(blocks) +
                       f"\n\033[90mUse: write: 1 {filename}\033[0m")
    
    def _list_blocks(self, blocks: List[Dict[str, str]]) -> str:
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
    
    def _write_single(self, block: Dict[str, str], filename: str, 
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
    
    def _write_all(self, blocks: List[Dict[str, str]], filename: str) -> str:
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
