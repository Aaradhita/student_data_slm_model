import sqlite3

DB_NAME = "students.db"

def get_student(student_name, register_number):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM students
        WHERE TRIM(Register_Number) = TRIM(?)
        AND LOWER(TRIM(Student_Name)) = LOWER(TRIM(?))
    """, (register_number, student_name))

    student = cursor.fetchone()
    conn.close()
    return student
    student = cursor.fetchone()
    conn.close()

    # Optional name verification (soft check)
    if student and student[0].strip().lower() == student_name.strip().lower():
        return student
