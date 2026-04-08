from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pandas as pd

class SLMIntentClassifier:
    def __init__(self):
        data = pd.read_csv("intent_data.csv")

        self.vectorizer = TfidfVectorizer()
        X = self.vectorizer.fit_transform(data["text"])
        y = data["intent"]

        self.model = LogisticRegression()
        self.model.fit(X, y)

    def predict_intent(self, text):
        vec = self.vectorizer.transform([text])
        return self.model.predict(vec)[0]
