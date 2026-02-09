#!/usr/bin/env python3
"""Test script to verify error detection fix"""

import sys
sys.path.insert(0, '/home/ozkan/my_ai_agent')

from groq_chat import SeniorAIEngineer

# Create test instance
engineer = SeniorAIEngineer()

print("=" * 70)
print("TESTING ERROR DETECTION FIX")
print("=" * 70)

# Test 1: File with "Error" in content (groq_chat.py itself)
print("\n📝 Test 1: Reading groq_chat.py (contains 'Error' keyword)")
print("-" * 70)

test_input_1 = "read: groq_chat.py"
read_pos = test_input_1.lower().find("read:")
after_read = test_input_1[read_pos + 5:].strip()
potential_file = after_read.split()[0].rstrip('.')

file_data = engineer.read_file_content(potential_file)

if file_data.startswith("[FILE_READ_ERROR]"):
    print("❌ FAILED: File read returned error")
    print(file_data.replace("[FILE_READ_ERROR]", ""))
else:
    print("✅ PASSED: File read successfully")
    print(f"   File size: {len(file_data)} characters")
    print(f"   Contains 'Error' keyword: {'Error' in file_data}")

# Test 2: Non-existent file
print("\n📝 Test 2: Reading non-existent file")
print("-" * 70)

file_data_2 = engineer.read_file_content("non_existent_file.py")

if file_data_2.startswith("[FILE_READ_ERROR]"):
    print("✅ PASSED: Correctly detected as error")
    print(f"   Error message: {file_data_2.replace('[FILE_READ_ERROR]', '').strip()[:50]}...")
else:
    print("❌ FAILED: Should have returned error")

print("\n" + "=" * 70)
print("ALL TESTS COMPLETED")
print("=" * 70)
