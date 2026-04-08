import sqlite3

conn = sqlite3.connect('students_2024.db')
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in students_2024.db:")
for t in tables:
    print(f"  {t[0]}")

# Check students table if it exists
try:
    cursor.execute("PRAGMA table_info(students)")
    cols = cursor.fetchall()
    if cols:
        print("\nStudents table columns in students_2024.db:")
        for c in cols:
            print(f"  {c[1]}: {c[2]}")
        
        # Count records
        cursor.execute("SELECT COUNT(*) FROM students")
        count = cursor.fetchone()[0]
        print(f"  Total records: {count}")
except:
    print("\nNo students table in students_2024.db")

conn.close()
