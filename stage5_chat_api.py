from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import uvicorn
import sqlite3


from stage4.rag_pipeline import rag_answer

app = FastAPI(
    title="Stage 5 – Student Support Chatbot",
    description="Browser-based chatbot combining intent detection, DB lookup, and RAG",
    version="1.0"
)

templates = Jinja2Templates(directory="templates")

STAGE3_API_URL = "http://127.0.0.1:8000"


def detect_intent(query: str):
    q = query.lower()
    if any(word in q for word in ["fee", "attendance", "cgpa", "academic", "scholarship", "my","Attendance","ATTENDANCE","Attendence","attendence","Fees","FEES","fees","CGPA","Scholarship","SCHOLARSHIP","ACADEMIC","Academic","academic","ATTENDENCE"]):
        return "student"
    return "faq"


@app.get("/", response_class=HTMLResponse)
def chat_ui(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@app.get("/chat")
def chat(message: str, student_name: str = "", register_number: str = ""):
    intent = detect_intent(message)

    # ---------- STUDENT QUERIES ----------
    if intent == "student":
        if not student_name or not register_number:
            return {"reply": "Please enter your name and register number."}

        if "fee" in message:
            endpoint = "/student/fees"
        elif "attendance" in message:
            endpoint = "/student/attendance"
        elif "cgpa" in message or "academic" in message:
            endpoint = "/student/academic"
        elif "scholarship" in message:
            endpoint = "/student/scholarship"
        elif "Attendence" in message:
            endpoint = "/student/attendance"
        elif "ATTENDENCE" in message:
            endpoint = "/student/attendance"
        elif "attendence" in message:
            endpoint = "/student/attendance"
        elif "Attendance" in message:
            endpoint = "/student/attendance"
        elif "ATTENDANCE" in message:
            endpoint = "/student/attendance"
        elif "Fees" in message:
            endpoint = "/student/fees"
        elif "FEES" in message:
            endpoint = "/student/fees"
        elif "fees" in message:
            endpoint = "/student/fees"
        elif "CGPA" in message:
            endpoint = "/student/academic"
        elif "Scholarship" in message:
            endpoint = "/student/scholarship"
        elif "SCHOLARSHIP" in message:
            endpoint = "/student/scholarship"
        elif "ACADEMIC" in message:
            endpoint = "/student/academic"
        elif "Academic" in message:
            endpoint = "/student/academic"
        elif "academic" in message:
            endpoint = "/student/academic"
        else:
            return {"reply": "Sorry, I could not identify your request."}

        response = requests.get(
            STAGE3_API_URL + endpoint,
            params={
                "student_name": student_name,
                "register_number": register_number
            }
        )

        if response.status_code != 200:
            return {"reply": "Student not found. Please check your details."}

        data = response.json()

        # ---------- CHATBOT RESPONSE FORMATTING ----------
        if "fees_details" in data:
            reply = (
                f"Hi {data['student_name']}, "
                f"your fee status is {data['fees_status']}. "
                f"Details: {data['fees_details']}."
            )

        elif "attendance_percentage" in data:
            reply = (
                f"Hi {data['student_name']}, "
                f"your attendance percentage is {data['attendance_percentage']}%."
            )

        elif "cgpa" in data:
            reply = (
                f"Hi {data['student_name']}, "
                f"your CGPA is {data['cgpa']}. "
                f"You are enrolled in {data['major']} under the {data['faculty']} faculty."
            )

        elif "scholarship_eligibility" in data:
            reply = (
                f"Hi {data['student_name']}, "
                f"your scholarship eligibility status is "
                f"{data['scholarship_eligibility']}."
            )

        else:
            reply = "Your record was found, but I could not format the response."

        return {"reply": reply}

    # ---------- FAQ / GENERAL QUERIES ----------
    else:
        return {"reply": rag_answer(message)}
@app.get("/students/search")
def search_students(query: str):
    if len(query) < 2:
        return []

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT Student_Name, Register_Number
        FROM students
        WHERE LOWER(Student_Name) LIKE ?
        LIMIT 5
    """, (query.lower() + "%",))

    results = [
        {"name": row[0], "register": row[1]}
        for row in cursor.fetchall()
    ]
    conn.close()
    return results

if __name__ == "__main__":
    uvicorn.run(
        "stage5_chat_api:app",
        host="127.0.0.1",
        port=9000,
        reload=False
    )
