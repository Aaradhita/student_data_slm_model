import pandas as pd
import sqlite3

df = pd.read_excel("student_dataset.xlsx")

df.columns = df.columns.str.strip()

df = df[[
    "Student_Name",
    "Register_Number",
    "Fees_Details",
    "Fees_Status",
    "Attendance_Percentage",
    "Books_Borrowed",
    "Scholarship_Eligibility",
    "Contact_Number",
    "Email_ID",
    "Date_of_Birth",
    "Faculty",
    "CGPA",
    "College_Joining_Date",
    "Major"
]]

df = df.where(pd.notnull(df), None)

conn = sqlite3.connect("students.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM students")
conn.commit()

try:
    for _, row in df.iterrows():
        cursor.execute("""
        INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(row))
    conn.commit()
    print("✅ Dataset successfully loaded into database.")
except Exception as e:
    print("❌ REAL SQLITE ERROR:", e)
finally:
    conn.close()
