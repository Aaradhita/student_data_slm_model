import sqlite3

conn = sqlite3.connect('students_2024.db')
cursor = conn.cursor()

# Check how many users in users table
cursor.execute("SELECT COUNT(*) FROM users")
user_count = cursor.fetchone()[0]
print(f"Total users in database: {user_count}")

# Check some sample register numbers
cursor.execute("SELECT register_number FROM users LIMIT 5")
samples = cursor.fetchall()
print("\nSample register numbers in database:")
for s in samples:
    print(f"  {s[0]}")

conn.close()
