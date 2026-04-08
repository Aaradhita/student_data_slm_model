import sqlite3

conn = sqlite3.connect('students_2024.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE users ADD COLUMN reset_token TEXT")
    print("✓ Added reset_token column")
except sqlite3.OperationalError as e:
    print(f"reset_token column: {e}")

try:
    cursor.execute("ALTER TABLE users ADD COLUMN reset_token_expires TIMESTAMP")
    print("✓ Added reset_token_expires column")
except sqlite3.OperationalError as e:
    print(f"reset_token_expires column: {e}")

conn.commit()
conn.close()

print("\n✓ Database migration complete!")
