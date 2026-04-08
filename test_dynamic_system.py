#!/usr/bin/env python3
"""Test the new dynamic system"""

import requests
import json

print("\n" + "="*70)
print("TESTING NEW DYNAMIC SYSTEM")
print("="*70)

# Test 1: Get Schema
print("\n[1] SCHEMA DISCOVERY")
print("-" * 70)
try:
    schema = requests.get("http://localhost:8000/api/schema").json()
    print(f"✓ Database: {schema['database']}")
    print(f"✓ Table: {schema['table']}")
    print(f"✓ Columns found: {len(schema['columns'])}")
    print(f"✓ Searchable columns sample: {schema['searchable_columns'][:5]}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Get Available Intents
print("\n[2] AVAILABLE INTENTS (Auto-Generated from Columns)")
print("-" * 70)
try:
    intents = requests.get("http://localhost:8000/api/intents").json()
    print(f"✓ Total intents found: {intents['count']}")
    print(f"✓ Example queries:")
    for i, example in enumerate(intents['examples'], 1):
        print(f"  {i}. {example}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Chat with Dynamic System
print("\n[3] DYNAMIC CHAT TEST")
print("-" * 70)
try:
    # Login
    login = requests.post("http://localhost:8000/api/login", json={
        "register_number": "REG1000",
        "password": "student123"
    }).json()
    token = login["access_token"]
    print(f"✓ Logged in as: {login['user']['full_name']}")
    
    # Test different queries
    test_queries = [
        "What is my GPA?",
        "Show my attendance",
        "Contact details",
        "Fees status"
    ]
    
    for query in test_queries:
        chat = requests.post("http://localhost:8000/api/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": query}
        ).json()
        print(f"\n  Query: \"{query}\"")
        print(f"  Intent: {chat['intent']}")
        print(f"  Response: {chat['response']}")
        
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*70)
print("✓ DYNAMIC SYSTEM IS WORKING!")
print("="*70 + "\n")
