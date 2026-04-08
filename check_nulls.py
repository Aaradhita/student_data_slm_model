import sqlite3

conn = sqlite3.connect('students_2024.db')
cursor = conn.cursor()

# Check for NULL register numbers
cursor.execute("SELECT COUNT(*) FROM students WHERE Register_Number IS NULL")
null_count = cursor.fetchone()[0]
print(f"Records with NULL Register_Number: {null_count}")

# Check for empty strings
cursor.execute("SELECT COUNT(*) FROM students WHERE Register_Number = ''")
empty_count = cursor.fetchone()[0]
print(f"Records with empty Register_Number: {empty_count}")

# Get total
cursor.execute("SELECT COUNT(*) FROM students")
total = cursor.fetchone()[0]
print(f"Total students: {total}")

# Show some NULL ones if they exist
if null_count > 0:
    cursor.execute("SELECT Student_Name, Register_Number FROM students WHERE Register_Number IS NULL LIMIT 5")
    print("\nSample NULL register_number records:")
    for row in cursor.fetchall():
        print(f"  {row}")

conn.close()
