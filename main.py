from embedding_intent_classifier import EmbeddingIntentClassifier
from db_utils import get_student

# Initialize SLM intent classifier
classifier = EmbeddingIntentClassifier()

print("🤖 Bot: Hi 👋 Welcome to the Student Support Chatbot!\n")

print("🤖 Bot: You can ask about the following topics:")
print("🤖 • Attendance (attendance, attendance percentage)")
print("🤖 • Academic details (academic, cgpa, major)")
print("🤖 • Scholarship (scholarship, eligibility)")
print("🤖 • Fees (fee details, fee status)\n")
print("🤖 Bot: To exit the chat, type 'exit' or 'quit'.\n")
while True:
    user_text = input("You: ")

    if user_text.lower() in ["exit", "quit"]:
        print("🤖 Bot: Thank you! Goodbye 😊")
        break

    # -------- Stage 2: Intent Identification (SLM) --------
    intent = classifier.predict_intent(user_text)
    print(f"🤖 Bot: Detected intent → {intent}")

    # -------- User Verification --------
    student_name = input("🤖 Bot: Enter your Name: ")
    register_number = input("🤖 Bot: Enter your Register Number: ")

    student = get_student(student_name, register_number)

    if not student:
        print("🤖 Bot: ❌ No matching student record found.\n")
        continue

    (
        name, reg_no,
        fees_details, fees_status,
        attendance, books_borrowed,
        scholarship, contact,
        email, dob,
        faculty, cgpa,
        joining_date, major
    ) = student

    # -------- Stage 3: DB Retrieval --------
    if intent == "fee_enquiry":
        print("🤖 Bot: Fees Details:", fees_details)
        print("🤖 Bot: Fees Status:", fees_status)

    elif intent == "attendance":
        print("🤖 Bot: Attendance Percentage:", attendance)

    elif intent == "academic":
        print("🤖 Bot: CGPA:", cgpa)
        print("🤖 Bot: Major:", major)
        print("🤖 Bot: Faculty:", faculty)

    elif intent == "scholarship":
        print("🤖 Bot: Scholarship Eligibility:", scholarship)

    else:
        print("🤖 Bot: Sorry, I couldn’t understand your request.")

    print()  # spacing