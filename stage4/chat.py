from rag_pipeline import rag_answer

print("📘 FAQ Support System (Stage 4)")
print("Ask a question or type 'exit' to quit\n")

while True:
    user_question = input("User: ")

    if user_question.lower() == "exit":
        print("System: Thank you! Goodbye.")
        break

    answer = rag_answer(user_question)
    print("System:", answer)
    print()