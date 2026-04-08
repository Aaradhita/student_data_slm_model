import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class EmbeddingIntentClassifier:
    def __init__(self):
        data = pd.read_csv("intent_data.csv")

        self.texts = data["text"].tolist()
        self.intents = data["intent"].tolist()

        # TF-IDF embeddings (lightweight SLM)
        self.vectorizer = TfidfVectorizer()
        self.embeddings = self.vectorizer.fit_transform(self.texts)

    def predict_intent(self, user_text):
        user_vec = self.vectorizer.transform([user_text])
        similarity = cosine_similarity(user_vec, self.embeddings)[0]
        best_idx = similarity.argmax()
        return self.intents[best_idx]
