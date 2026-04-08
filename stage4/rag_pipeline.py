import faiss
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load FAISS index and assets
index = faiss.read_index(os.path.join(ROOT_DIR, "faq_index.faiss"))

with open(os.path.join(ROOT_DIR, "faq_docs.pkl"), "rb") as f:
    documents = pickle.load(f)

with open(os.path.join(ROOT_DIR, "tfidf_vectorizer.pkl"), "rb") as f:
    vectorizer: TfidfVectorizer = pickle.load(f)


# -------- HARD GUARANTEE LAYER --------
def keyword_match(query):
    q = query.lower()

    for doc in documents:
        if q.split()[0] in doc.lower():
            return doc.split(":", 1)[1].strip()

    return None


# -------- FAISS FALLBACK --------
def retrieve_context(query):
    query_vector = vectorizer.transform([query]).toarray()
    _, indices = index.search(query_vector, 1)
    return documents[indices[0][0]].split(":", 1)[1].strip()


def rag_answer(user_query):
    # 1️⃣ keyword-based precision
    exact = keyword_match(user_query)
    if exact:
        return "Based on the available information: " + exact

    # 2️⃣ vector-based fallback
    return "Based on the available information: " + retrieve_context(user_query)
