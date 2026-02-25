import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Load dataset
data = pd.read_csv("spam.csv")
data['label'] = data['label'].map({'ham': 0, 'spam': 1})

X = data['text']
y = data['label']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Vectorization
vectorizer = TfidfVectorizer(stop_words='english')
X_train_vec = vectorizer.fit_transform(X_train)

# Train model
model = MultinomialNB()
model.fit(X_train_vec, y_train)

# Prediction function
def predict_email(email_text):
    email_vec = vectorizer.transform([email_text])
    result = model.predict(email_vec)
    return "Spam" if result[0] == 1 else "Not Spam"
