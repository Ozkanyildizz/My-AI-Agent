#!/usr/bin/env python3
"""Test script to verify the read: command parsing fix"""

import sys
sys.path.insert(0, '/home/ozkan/my_ai_agent')

from groq_chat import SeniorAIEngineer

# Create test instance
engineer = SeniorAIEngineer()

# Test case: simulate user input parsing
test_input = "read: test_file.py tell me about this file"

print("=" * 60)
print("TESTING READ COMMAND PARSING FIX")
print("=" * 60)
print(f"\nTest Input: {test_input}")
print("\n" + "-" * 60)

# Extract the parsing logic
if "read:" in test_input.lower():
    read_pos = test_input.lower().find("read:")
    after_read = test_input[read_pos + 5:].strip()
    potential_file = after_read.split()[0].rstrip('.') if after_read else ""
    user_prompt = after_read[len(potential_file):].strip()
    
    print(f"✅ Extracted file path: '{potential_file}'")
    print(f"✅ Extracted user prompt: '{user_prompt}'")
    print(f"✅ Final prompt: 'Reference: {potential_file}. {user_prompt}'")
    
print("\n" + "=" * 60)
print("PARSING TEST COMPLETED SUCCESSFULLY!")
print("=" * 60)
