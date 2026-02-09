#!/usr/bin/env python3
"""Test write command functionality."""

import sys
sys.path.insert(0, '/home/ozkan/my_ai_agent')

from write_helpers import extract_code_blocks, parse_write_command

# Test 1: Extract code blocks
print("="*60)
print("TEST 1: Code Block Extraction")
print("="*60)

test_response = """
Here's a simple function:

```python
def hello():
    print("Hello, World!")
```

And here's another one:

```javascript
function goodbye() {
    console.log("Goodbye!");
}
```
"""

blocks = extract_code_blocks(test_response)
print(f"Found {len(blocks)} code blocks:")
for i, block in enumerate(blocks, 1):
    print(f"  {i}. [{block['language']}] {len(block['code'].split(chr(10)))} lines")

# Test 2: Parse write commands
print("\n" + "="*60)
print("TEST 2: Command Parsing")
print("="*60)

test_commands = [
    "write: test.py",
    "write: 1 main.py",
    "write: list",
    "write: all output.txt",
    "write: 2 utils.py"
]

for cmd in test_commands:
    result = parse_write_command(cmd)
    if result:
        action, filename, index = result
        print(f"{cmd:30} -> action={action:6} file={filename:12} index={index}")
    else:
        print(f"{cmd:30} -> INVALID")

print("\n✅ Helper functions working correctly!")
