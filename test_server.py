#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("[TEST 1] Login")
print("=" * 60)

try:
    response = requests.post(
        f"{BASE_URL}/api/login",
        json={"register_number": "DEMO001", "password": "demo@123"},
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if "access_token" in data:
        token = data["access_token"]
        print(f"\n✓ Login successful")
        print(f"Token: {token[:50]}...")
        
        print("\n" + "=" * 60)
        print("[TEST 2] Chat - What's my GPA?")
        print("=" * 60)
        
        chat_response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"message": "What is my GPA?"},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
        )
        print(f"Status: {chat_response.status_code}")
        chat_data = chat_response.json()
        print(f"Response: {json.dumps(chat_data, indent=2)}")
        
    else:
        print("✗ No token in response")
except Exception as e:
    print(f"✗ Error: {e}")
