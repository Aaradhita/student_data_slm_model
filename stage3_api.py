from fastapi import FastAPI, HTTPException
from db_utils import get_student
from fastapi.responses import RedirectResponse
import uvicorn
from pydantic import BaseModel

app = FastAPI(
    title="Stage 3 – Student Database Retrieval API",
    description="FastAPI service for retrieving student information from SQLite",
    version="1.0"
)
@app.get("/")
def root():
    return RedirectResponse(url="/docs")


@app.get("/student/fees")
def get_fee_details(register_number: str, student_name: str):
    student = get_student(student_name, register_number)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return {
        "student_name": student[0],
        "register_number": student[1],
        "fees_details": student[2],
        "fees_status": student[3]
    }


@app.get("/student/attendance")
def get_attendance(register_number: str, student_name: str):
    student = get_student(student_name, register_number)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return {
        "student_name": student[0],
        "attendance_percentage": student[4]
    }


@app.get("/student/academic")
def get_academic_details(register_number: str, student_name: str):
    student = get_student(student_name, register_number)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return {
        "student_name": student[0],
        "cgpa": student[11],
        "faculty": student[10],
        "major": student[13]
    }


@app.get("/student/scholarship")
def get_scholarship_status(register_number: str, student_name: str):
    student = get_student(student_name, register_number)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return {
        "student_name": student[0],
        "scholarship_eligibility": student[6]
    }

@app.get("/student/books")
def get_books_borrowed(register_number: str, student_name: str):
    student = get_student(student_name, register_number)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {
        "student_name": student[0],
        "books_borrowed": student[5]
    }

@app.get("/student/contact")
def get_contact_number(register_number: str, student_name: str):
    student = get_student(student_name, register_number)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {
        "student_name": student[0],
        "contact_number": student[7]
    }

@app.get("/student/email")
def get_email_id(register_number: str, student_name: str):
    student = get_student(student_name, register_number)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {
        "student_name": student[0],
        "email_id": student[8]
    }

if __name__ == "__main__":
    uvicorn.run(
        "stage3_api:app",
        host="127.0.0.1",
        port=8000,
        reload=False
    )

