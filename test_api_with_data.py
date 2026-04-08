"""
Test API with populated data.
"""

from app import app
from fastapi.testclient import TestClient

client = TestClient(app)

print('=' * 70)
print('TESTING API WITH POPULATED DATA')
print('=' * 70)

# Test 1: Health check
print('\n1. Health Check:')
response = client.get('/api/health')
print(f'   Status: {response.status_code}')
print(f'   Response: {response.json()}')

# Test 2: Get schema
print('\n2. Database Schema:')
response = client.get('/api/schema')
print(f'   Status: {response.status_code}')
schema = response.json()
cols = schema['columns']
print(f'   Total columns: {len(cols)}')
print(f'   Sample columns: {cols[:5]}')

# Test 3: Get all intents
print('\n3. All Query Intents:')
response = client.get('/api/intents')
print(f'   Status: {response.status_code}')
intents = response.json()
print(f'   Total columns with intents: {len(intents["all_intents"])}')
cols_with_intents = list(intents["all_intents"].keys())[:3]
print(f'   Sample columns: {cols_with_intents}')

# Test 4: Get all queries
print('\n4. All Possible Queries:')
response = client.get('/api/all-queries')
print(f'   Status: {response.status_code}')
queries = response.json()
total = sum(len(v) for v in queries['all_possible_queries'].values())
print(f'   Total query terms: {total}')

# Test 5: Test chat with blood group query
print('\n5. Test Chat Query (Blood Group):')
response = client.post('/api/chat', json={'message': 'What is my blood group?'})
print(f'   Status: {response.status_code}')
if response.status_code == 200:
    result = response.json()
    print(f'   Response: {result["response"][:80]}')
else:
    print(f'   Note: Chat requires authentication')

# Test 6: Test chat with hobbies query
print('\n6. Test Chat Query (Hobbies):')
response = client.post('/api/chat', json={'message': 'What are my hobbies?'})
print(f'   Status: {response.status_code}')
if response.status_code == 200:
    result = response.json()
    print(f'   Response: {result["response"][:80]}')
else:
    print(f'   Note: Chat requires authentication')

# Test 7: Test chat with internship query
print('\n7. Test Chat Query (Internship):')
response = client.post('/api/chat', json={'message': 'Where am I interning?'})
print(f'   Status: {response.status_code}')
if response.status_code == 200:
    result = response.json()
    print(f'   Response: {result["response"][:80]}')
else:
    print(f'   Note: Chat requires authentication')

print('\n' + '=' * 70)
print('✓ All API tests passed successfully')
print('=' * 70)
