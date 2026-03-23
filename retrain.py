import os
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import pickle

def train_model():
    dataset_path = 'data/dialysis_dataset_enhanced.csv'
    if not os.path.exists(dataset_path):
        print("Dataset not found!")
        return None
    
    df = pd.read_csv(dataset_path)
    # Training with enhanced medical parameters including GFR
    features = ['potassium', 'sodium', 'urea', 'creatinine', 'sugar', 'hgb', 'fluid', 'gfr']
    X = df[features]
    y = df['risk_level']
    
    model = DecisionTreeClassifier()
    model.fit(X, y)
    
    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)
    print("Model retrained successfully with enhanced data.")
    return model

if __name__ == "__main__":
    train_model()
