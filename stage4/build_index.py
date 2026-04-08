import faiss
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer


# Load FAQ documents
with open("stage4/faqs.txt", "r", encoding="utf-8") as f:
    documents = [line.strip() for line in f if line.strip()]

# Create TF-IDF vectorizer
vectorizer = TfidfVectorizer(stop_words="english")
tfidf_vectors = vectorizer.fit_transform(documents).toarray()

# Build FAISS index
dimension = tfidf_vectors.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(tfidf_vectors)

# Save index and vectorizer
faiss.write_index(index, "faq_index.faiss")
with open("faq_docs.pkl", "wb") as f:
    pickle.dump(documents, f)
with open("tfidf_vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("✅ FAISS index built using TF-IDF embeddings")
