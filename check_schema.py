import sqlite3

conn = sqlite3.connect('students_2024.db')
cursor = conn.cursor()

# Check users table columns
cursor.execute("PRAGMA table_info(users)")
cols = cursor.fetchall()

print("Users table columns:")
for c in cols:
    print(f"  {c[1]}: {c[2]}")

conn.close()
