import sqlite3

conn = sqlite3.connect('students.db')
cursor = conn.cursor()

# Check students table columns
cursor.execute("PRAGMA table_info(students)")
cols = cursor.fetchall()

print("Students table columns:")
for c in cols:
    print(f"  {c[1]}: {c[2]}")

# Check a few sample records
print("\nSample records:")
cursor.execute("SELECT * FROM students LIMIT 3")
for row in cursor.fetchall():
    print(row)

conn.close()
