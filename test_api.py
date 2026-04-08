#!/usr/bin/env python
"""
Quick test script to verify the Student Portal is working correctly
Run: python test_api.py
"""

import requests
import json
import time
from typing import Dict, Tuple

API_URL = "http://localhost:8000"
TIMEOUT = 5

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_result(test_name: str, passed: bool, message: str = ""):
    """Print test result"""
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    message_text = f" - {message}" if message else ""
    print(f"  {status}: {test_name}{message_text}")
    return passed

def test_health() -> bool:
    """Test health endpoint"""
    try:
        response = requests.get(f"{API_URL}/api/health", timeout=TIMEOUT)
        return print_result("Health Check", response.status_code == 200, f"Status {response.status_code}")
    except Exception as e:
        return print_result("Health Check", False, str(e))

def test_login() -> Tuple[bool, str]:
    """Test login endpoint"""
    try:
        data = {
            "register_number": "DEMO001",
            "password": "demo@123"
        }
        response = requests.post(f"{API_URL}/api/login", json=data, timeout=TIMEOUT)
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            return print_result("Login", True, "Token received"), token
        else:
            return print_result("Login", False, f"Status {response.status_code}"), ""
    except Exception as e:
        return print_result("Login", False, str(e)), ""

def test_profile(token: str) -> bool:
    """Test profile endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/api/user/profile", headers=headers, timeout=TIMEOUT)
        return print_result("Get Profile", response.status_code == 200, f"Status {response.status_code}")
    except Exception as e:
        return print_result("Get Profile", False, str(e))

def test_chat(token: str, message: str) -> bool:
    """Test chat endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {"message": message}
        response = requests.post(f"{API_URL}/api/chat", json=data, headers=headers, timeout=TIMEOUT)
        
        if response.status_code == 200:
            result = response.json()
            return print_result(
                f"Chat Query", 
                True, 
                f"Intent: {result.get('intent', 'unknown')}"
            )
        else:
            return print_result("Chat Query", False, f"Status {response.status_code}")
    except Exception as e:
        return print_result("Chat Query", False, str(e))

def test_unauthorized() -> bool:
    """Test unauthorized access"""
    try:
        response = requests.get(f"{API_URL}/api/user/profile", timeout=TIMEOUT)
        return print_result("Unauthorized Block", response.status_code == 401, "Correctly blocked")
    except Exception as e:
        return print_result("Unauthorized Block", False, str(e))

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 STUDENT PORTAL - API TEST SUITE")
    print("="*60 + "\n")
    
    # Check if server is running
    print("📍 Checking server connection...")
    try:
        requests.get(f"{API_URL}/api/health", timeout=TIMEOUT)
        print(f"   {Colors.GREEN}✓{Colors.END} Server is running at {API_URL}\n")
    except:
        print(f"   {Colors.RED}✗{Colors.END} Cannot connect to server!")
        print(f"   Please make sure the server is running: python app.py\n")
        return
    
    # Run tests
    print("🧪 Running Tests...\n")
    
    test_health()
    test_unauthorized()
    
    passed_login, token = test_login()
    
    if passed_login and token:
        test_profile(token)
        test_chat(token, "What's my GPA?")
        test_chat(token, "Show my fees")
        test_chat(token, "My attendance")
    
    print("\n" + "="*60)
    print("📊 ENDPOINTS AVAILABLE")
    print("="*60)
    print("  POST  /api/login              - User login")
    print("  POST  /api/register           - New user registration")
    print("  POST  /api/chat               - Send chat message (auth required)")
    print("  GET   /api/user/profile       - Get user profile (auth required)")
    print("  GET   /api/user/data/{col}    - Get column data (auth required)")
    print("  GET   /api/health             - Health check")
    print("\n" + "="*60)
    print("🌐 WEB INTERFACE")
    print("="*60)
    print(f"  Login:     {API_URL}/login.html")
    print(f"  Dashboard: {API_URL}/dashboard.html")
    print(f"  API Docs:  {API_URL}/docs")
    print("\n" + "="*60)
    print("📝 Demo Account")
    print("="*60)
    print("  Register: DEMO001")
    print("  Password: demo@123")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
