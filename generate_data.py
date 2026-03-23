import pandas as pd
import numpy as np
import os

def generate_dialysis_data(num_records=1200):
    np.random.seed(42)
    
    # Generate random data
    potassium = np.random.uniform(3.0, 7.5, num_records)
    sodium = np.random.uniform(125, 150, num_records)
    fluid = np.random.uniform(500, 3000, num_records)
    urea = np.random.uniform(20, 200, num_records)
    creatinine = np.random.uniform(0.5, 15, num_records)
    sugar = np.random.uniform(70, 250, num_records)
    hgb = np.random.uniform(7, 16, num_records)
    weight = np.random.uniform(45, 110, num_records)
    
    data = pd.DataFrame({
        'patient_id': np.arange(1, num_records + 1),
        'potassium': np.round(potassium, 2),
        'sodium': np.round(sodium, 2),
        'fluid': np.round(fluid, 2),
        'urea': np.round(urea, 2),
        'creatinine': np.round(creatinine, 2),
        'sugar': np.round(sugar, 2),
        'hgb': np.round(hgb, 2),
        'weight': np.round(weight, 2)
    })
    
    def classify_combined_risk(row):
        score = 0
        # Critical factors
        if row['potassium'] > 6.0 or row['potassium'] < 3.5: score += 4
        if row['creatinine'] > 8.0: score += 3
        if row['urea'] > 120: score += 2
        if row['hgb'] < 9.0: score += 2
        if row['fluid'] > 2500: score += 2
        
        if score >= 6: return 'High'
        if score >= 3: return 'Moderate'
        return 'Safe'
            
    data['risk_level'] = data.apply(classify_combined_risk, axis=1)
    
    # Add food safety indicator
    data['food_safe'] = data['potassium'].apply(lambda x: 'Yes' if x < 5.5 else 'No')
    
    # Create directory if not exists
    if not os.path.exists('data'):
        os.makedirs('data')
        
    # Save to CSV
    data.to_csv('data/dialysis_dataset.csv', index=False)
    print(f"Generated {num_records} records with comprehensive medical data.")

if __name__ == "__main__":
    generate_dialysis_data(1200)
