import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

# Ensure we run this in the correct directory
basedir = os.path.abspath(os.path.dirname(__file__))
data_path = os.path.join(basedir, "chat_data.csv")
model_path = os.path.join(basedir, "chat_model.pkl")
vectorizer_path = os.path.join(basedir, "vectorizer.pkl")

# Load dataset
print(f"Loading data from {data_path}...")
data = pd.read_csv(data_path)

# Features & labels
X = data['question']
y = data['intent']

# Vectorization
print("Training TF-IDF Vectorizer...")
vectorizer = TfidfVectorizer()
X_vec = vectorizer.fit_transform(X)

# Model
print("Training Random Forest Classifier...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_vec, y)

# Evaluate Accuracy
from sklearn.metrics import accuracy_score
y_pred = model.predict(X_vec)
accuracy = accuracy_score(y, y_pred)
print(f"Training Accuracy: {accuracy * 100:.2f}%")

# Save model
print("Saving model and vectorizer...")
with open(model_path, "wb") as f:
    pickle.dump(model, f)
with open(vectorizer_path, "wb") as f:
    pickle.dump(vectorizer, f)

print("Done! Chatbot model trained successfully.")
