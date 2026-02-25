import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Load dataset
data = pd.read_csv("spam.csv")

# Remove empty rows
data = data.dropna()

# Convert labels to lowercase
data["label"] = data["label"].str.lower()

# Convert spam/ham to numbers
data["label"] = data["label"].map({
    "ham": 0,
    "spam": 1
})

# Remove rows that failed mapping
data = data.dropna()

# Features and target
X = data["text"]
y = data["label"]

# Vectorization
vectorizer = TfidfVectorizer()
X_vec = vectorizer.fit_transform(X)

# Train model
model = MultinomialNB()
model.fit(X_vec, y)

# Prediction function
def predict_email(text):
    vec = vectorizer.transform([text])
    prediction = model.predict(vec)[0]
    return int(prediction)   # 1 = spam, 0 = ham