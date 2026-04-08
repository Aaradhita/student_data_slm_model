#!/usr/bin/env python3
"""
Test script for REAL-TIME Dynamic Intent System
Tests all columns are queryable with various query formats
"""

import requests
import json
import time
import sys

# Give server a moment to be ready
time.sleep(2)

# Test 1: Login
print("=" * 70)
print("TEST 1: Login as DEMO001")
print("=" * 70)
try:
    response = requests.post('http://localhost:8000/api/auth/login', json={
        'register_number': 'DEMO001',
        'password': 'demo@123'
    })
    if response.status_code == 200:
        data = response.json()
        token = data['access_token']
        print(f"✓ Login successful!")
        print(f"  Token: {token[:30]}...")
        
        # Test 2: Get Schema (REAL-TIME)
        print("\n" + "=" * 70)
        print("TEST 2: Get Database Schema (REAL-TIME Column Discovery)")
        print("=" * 70)
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get('http://localhost:8000/api/schema', headers=headers)
        if response.status_code == 200:
            schema = response.json()
            print(f"✓ Schema loaded successfully (REAL-TIME from database)!")
            print(f"  Total columns: {schema['total_columns']}")
            print(f"  Queryable columns: {schema['total_queryable']}")
            print(f"  Columns found: {', '.join(schema['columns'])}")
        else:
            print(f"✗ Failed to get schema: {response.status_code}")
        
        # Test 3: Get Intents (REAL-TIME)
        print("\n" + "=" * 70)
        print("TEST 3: Get All Intents (REAL-TIME Generation)")
        print("=" * 70)
        response = requests.get('http://localhost:8000/api/intents', headers=headers)
        if response.status_code == 200:
            intents = response.json()
            print(f"✓ Intents generated successfully (REAL-TIME)!")
            print(f"  Total intents: {intents['total_intents']}")
            print(f"  Sample queries generated:")
            for sample in intents['sample_queries'][:5]:
                print(f"    - {sample}")
        else:
            print(f"✗ Failed to get intents: {response.status_code}")
        
        # Test 4: All Possible Queries Endpoint
        print("\n" + "=" * 70)
        print("TEST 4: Show All Possible Queries (What user can ask)")
        print("=" * 70)
        response = requests.get('http://localhost:8000/api/all-queries', headers=headers)
        if response.status_code == 200:
            queries = response.json()
            print(f"✓ All possible queries retrieved!")
            print(f"  Queryable columns: {queries['total_queryable_columns']}")
            print(f"  Columns list: {', '.join(queries['queryable_columns'][:7])}...")
            # Show search terms for first 3 columns
            print(f"\n  Sample search terms for each column:")
            for col, terms in list(queries['all_possible_queries'].items())[:3]:
                print(f"    {col}: {', '.join(terms[:5])}")
        else:
            print(f"✗ Failed: {response.status_code}")
        
        # Test 5: Chat Query - Test different column queries
        print("\n" + "=" * 70)
        print("TEST 5: Chat Queries (Testing All Column Types)")
        print("=" * 70)
        
        test_queries = [
            ("What's my CGPA?", "CGPA"),
            ("Show my attendance", "Attendance_Percentage"),
            ("Fee details", "Fees_Details"),
            ("Contact information", "Contact_Number"),
            ("When was I born?", "Date_of_Birth"),
            ("What's my major?", "Major"),
            ("How many books have I borrowed?", "Books_Borrowed"),
            ("Scholarship eligibility", "Scholarship_Eligibility"),
            ("My faculty", "Faculty"),
            ("Email address please", "Email_ID"),
            ("Fees status", "Fees_Status"),
            ("College joining date", "College_Joining_Date"),
            ("My register number", "Register_Number"),
            ("Student name", "Student_Name"),
        ]
        
        success_count = 0
        for query, expected_column in test_queries:
            response = requests.post('http://localhost:8000/api/chat', 
                json={'message': query},
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                matched_column = data.get('intent', 'UNKNOWN')
                response_text = data.get('response', '')[:60]
                status = "✓" if matched_column == expected_column else "!"
                
                print(f"  {status} Q: {query}")
                print(f"      Expected: {expected_column}, Got: {matched_column}")
                print(f"      Response: {response_text}...")
                
                if matched_column == expected_column:
                    success_count += 1
            else:
                print(f"  ✗ Query failed: {query}")
        
        print(f"\n✓ Test Results: {success_count}/{len(test_queries)} queries matched correct columns")
        
    else:
        print(f"Login failed: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
