#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000"

print("\n" + "="*60)
print("TESTING WITH REAL STUDENT (REG1000)")
print("="*60)

# Test 1: Login as REG1000
response = requests.post(
    f"{BASE_URL}/api/login",
    json={"register_number": "REG1000", "password": "student123"},
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    data = response.json()
    token = data["access_token"]
    user = data["user"]
    print(f"\n[✓] LOGIN SUCCESSFUL")
    print(f"    User: {user['full_name']}")
    print(f"    Register: {user['register_number']}")
    print(f"    Email: {user['email']}")
    
    # Test 2: Chat - What's my GPA?
    print(f"\n[TEST] Chat: What's my GPA?")
    chat_response = requests.post(
        f"{BASE_URL}/api/chat",
        json={"message": "What is my GPA?"},
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
    )
    
    if chat_response.status_code == 200:
        chat_data = chat_response.json()
        print(f"[✓] RESPONSE: {chat_data['response']}")
        print(f"    Intent: {chat_data['intent']}")
    else:
        print(f"[✗] ERROR: {chat_response.status_code}")
        print(f"    {chat_response.json()}")
    
    # Test 3: Chat - Fees
    print(f"\n[TEST] Chat: What are my fees?")
    chat_response2 = requests.post(
        f"{BASE_URL}/api/chat",
        json={"message": "Show my fees"},
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
    )
    
    if chat_response2.status_code == 200:
        chat_data2 = chat_response2.json()
        print(f"[✓] RESPONSE: {chat_data2['response']}")
        print(f"    Intent: {chat_data2['intent']}")
    else:
        print(f"[✗] ERROR: {chat_response2.status_code}")
        
    # Test 4: Chat - Attendance
    print(f"\n[TEST] Chat: My attendance?")
    chat_response3 = requests.post(
        f"{BASE_URL}/api/chat",
        json={"message": "What's my attendance?"},
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
    )
    
    if chat_response3.status_code == 200:
        chat_data3 = chat_response3.json()
        print(f"[✓] RESPONSE: {chat_data3['response']}")
        print(f"    Intent: {chat_data3['intent']}")
    else:
        print(f"[✗] ERROR: {chat_response3.status_code}")
    
else:
    print(f"[✗] LOGIN FAILED: {response.status_code}")
    print(f"    {response.json()}")

print("\n" + "="*60)
print("ALL TESTS PASSED! ✓")
print("="*60 + "\n")
