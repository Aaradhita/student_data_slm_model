import sqlite3

print("=" * 60)
print("DATABASE STRUCTURE CHECK")
print("=" * 60)

# Check students.db
print("\n📊 Checking students.db...")
try:
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables: {tables}")
    
    if 'students' in tables:
        cursor.execute("SELECT * FROM students LIMIT 1")
        cols = [desc[0] for desc in cursor.description]
        print(f"Columns: {cols}")
        
        cursor.execute("SELECT COUNT(*) FROM students")
        count = cursor.fetchone()[0]
        print(f"✅ Total students: {count}")
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")

# Check students_2024.db
print("\n📊 Checking students_2024.db...")
try:
    conn = sqlite3.connect('students_2024.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables: {tables}")
    
    if 'users' in tables:
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        print(f"✅ Users table: {count} users")
    
    if 'students' in tables:
        cursor.execute("SELECT COUNT(*) FROM students")
        count = cursor.fetchone()[0]
        print(f"✅ Students table: {count} students")
    
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
