"""Helper methods for write command - code block extraction and file writing."""

import re
from typing import List, Dict, Optional, Tuple


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """
    Extract code blocks from markdown-formatted text.
    
    Args:
        text: Markdown text containing code blocks
        
    Returns:
        List of dicts with 'language' and 'code' keys
        
    Example:
        >>> text = '```python\\nprint("hello")\\n```'
        >>> extract_code_blocks(text)
        [{'language': 'python', 'code': 'print("hello")'}]
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


def parse_write_command(command: str) -> Optional[Tuple[str, str, Optional[int]]]:
    """
    Parse write: command into components.
    
    Args:
        command: User input starting with "write:"
        
    Returns:
        (action, filename, index) tuple or None
        - action: 'write', 'list', or 'all'
        - filename: target filename (or empty for 'list')
        - index: 1-based index or None
        
    Examples:
        >>> parse_write_command("write: test.py")
        ('write', 'test.py', None)
        
        >>> parse_write_command("write: 1 test.py")
        ('write', 'test.py', 1)
        
        >>> parse_write_command("write: list")
        ('list', '', None)
        
        >>> parse_write_command("write: all output.txt")
        ('all', 'output.txt', None)
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
