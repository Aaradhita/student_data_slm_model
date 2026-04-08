import sqlite3

conn = sqlite3.connect("students.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    Student_Name TEXT,
    Register_Number TEXT PRIMARY KEY,

    Fees_Details TEXT,
    Fees_Status TEXT,

    Attendance_Percentage REAL,
    Books_Borrowed INTEGER,

    Scholarship_Eligibility TEXT,
    Contact_Number TEXT,
    Email_ID TEXT,
    Date_of_Birth TEXT,

    Faculty TEXT,
    CGPA REAL,
    College_Joining_Date TEXT,
    Major TEXT
);
""")

conn.commit()
conn.close()

print("✅ students.db created with students table")
