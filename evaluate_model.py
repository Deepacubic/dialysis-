import os
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle

def evaluate_model():
    dataset_path = 'data/dialysis_dataset_enhanced.csv'
    if not os.path.exists(dataset_path):
        print("Dataset not found!")
        return
    
    df = pd.read_csv(dataset_path)
    features = ['potassium', 'sodium', 'urea', 'creatinine', 'sugar', 'hgb', 'fluid', 'gfr']
    X = df[features]
    y = df['risk_level']
    
    # Split for evaluation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = DecisionTreeClassifier(random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    conf_matrix = confusion_matrix(y_test, y_pred)
    
    print(f"--- Model Evaluation Results ---")
    print(f"Algorithm: Decision Tree Classifier")
    print(f"Total Samples: {len(df)}")
    print(f"Training Samples: {len(X_train)}")
    print(f"Testing Samples: {len(X_test)}")
    print(f"Accuracy: {accuracy * 100:.2f}%")
    print("\nClassification Report:")
    print(report)
    print("\nConfusion Matrix:")
    print(conf_matrix)
    
    # Save the model for consistency
    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)
        
if __name__ == "__main__":
    evaluate_model()
