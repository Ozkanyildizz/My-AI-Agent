#!/usr/bin/env python3
"""
Quick test script for refactored groq_chat.py
Tests all core functionality without interactive loop.
"""

import sys
sys.path.insert(0, '/home/ozkan/my_ai_agent')

from groq_chat import SeniorAIEngineer
from config import Config

print("=" * 70)
print("PHASE 1 REFACTORING VERIFICATION TESTS")
print("=" * 70)

# Test 1: Initialization
print("\\n📝 Test 1: Initialization")
print("-" * 70)
try:
    config = Config()
    engineer = SeniorAIEngineer(config)
    print("✅ PASSED: SeniorAIEngineer initialized successfully")
    print(f"   Config loaded: model={config.model}")
except Exception as e:
    print(f"❌ FAILED: {e}")
    sys.exit(1)

# Test 2: File reading
print("\\n📝 Test 2: File Reading")
print("-" * 70)
try:
    result = engineer.read_file_content("test_file.py")
    if not result.startswith("[FILE_READ_ERROR]"):
        print("✅ PASSED: File read successfully")
        print(f"   File size: {len(result)} characters")
    else:
        print(f"❌ FAILED: {result}")
except Exception as e:
    print(f"❌ FAILED: {e}")

# Test 3: Parse read command
print("\\n📝 Test 3: Parse Read Command")
print("-" * 70)
try:
    test_input = "read: test.py analyze this file"
    result = engineer._parse_read_command(test_input)
    if result and result[0] == "test.py" and "analyze" in result[1]:
        print("✅ PASSED: Command parsed correctly")
        print(f"   File: {result[0]}, Prompt: {result[1]}")
    else:
        print(f"❌ FAILED: Unexpected result: {result}")
except Exception as e:
    print(f"❌ FAILED: {e}")

# Test 4: Lesson logging
print("\\n📝 Test 4: Lesson Logging")
print("-" * 70)
try:
    result = engineer.log_lesson("Test lesson from refactored code")
    if "Successfully" in result:
        print("✅ PASSED: Lesson logged")
        print(f"   {result}")
    else:
        print(f"❌ FAILED: {result}")
except Exception as e:
    print(f"❌ FAILED: {e}")

# Test 5: History management
print("\\n📝 Test 5: History Management")
print("-" * 70)
try:
    initial_len = len(engineer.history)
    # Add many messages to trigger sliding window
    for i in range(25):
        engineer.history.append({"role": "user", "content": f"message {i}"})
    
    engineer._manage_history(False)
    final_len = len(engineer.history)
    
    if final_len <= config.max_history:
        print("✅ PASSED: History managed correctly")
        print(f"   Initial: {initial_len}, After adding 25: {final_len}")
    else:
        print(f"❌ FAILED: History not trimmed. Length: {final_len}")
except Exception as e:
    print(f"❌ FAILED: {e}")

print("\\n" + "=" * 70)
print("VERIFICATION TESTS COMPLETED")
print("=" * 70)
