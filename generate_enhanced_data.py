import pandas as pd
import numpy as np
import os

def generate_enhanced_kidney_data(num_records=1000):
    np.random.seed(42)
    
    # Define condition types and their relative frequency
    condition_types = [
        'CKD Stage 1', 'CKD Stage 2', 'CKD Stage 3', 'CKD Stage 4', 'CKD Stage 5 (ESRD)',
        'AKI (Acute Kidney Injury)', 'Hemodialysis', 'Peritoneal Dialysis',
        'Post-Transplant', 'Diabetic Kidney Disease', 'Hypertensive Kidney Disease',
        'Genetic (PKD/Alport)', 'Kidney Stones', 'Glomerulonephritis', 'Pediatric'
    ]
    
    # Create empty list for records
    records = []
    
    for i in range(1, num_records + 1):
        # Weighted selection of conditions (more CKD and Dialysis common in India/Global)
        condition = np.random.choice(condition_types, p=[
            0.05, 0.05, 0.10, 0.10, 0.15, # CKD 1-5
            0.10, 0.10, 0.05,             # AKI, HD, PD
            0.05, 0.10, 0.05,             # Transplant, Diabetes, Hypertension
            0.02, 0.03, 0.03, 0.02              # Genetic, Stones, GN, Pediatric
        ])
        
        age = np.random.randint(18, 85) if condition != 'Pediatric' else np.random.randint(1, 17)
        
        # Medical Parameters default ranges
        potassium = np.random.uniform(3.5, 5.0)
        sodium = np.random.uniform(135, 145)
        urea = np.random.uniform(20, 40)
        creatinine = np.random.uniform(0.6, 1.2)
        hgb = np.random.uniform(12, 16)
        sugar = np.random.uniform(70, 120)
        fluid = np.random.uniform(1500, 2500)
        
        # Adjust parameters based on condition
        if 'CKD Stage 1' in condition:
            creatinine = np.random.uniform(0.8, 1.2)
            gfr = np.random.uniform(90, 120)
        elif 'CKD Stage 2' in condition:
            creatinine = np.random.uniform(1.2, 1.5)
            gfr = np.random.uniform(60, 89)
        elif 'CKD Stage 3' in condition:
            creatinine = np.random.uniform(1.5, 2.5)
            gfr = np.random.uniform(30, 59)
            potassium += 0.5
            urea += 20
            hgb -= 2
        elif 'CKD Stage 4' in condition:
            creatinine = np.random.uniform(2.5, 5.0)
            gfr = np.random.uniform(15, 29)
            potassium += 1.0
            urea += 40
            hgb -= 4
        elif 'CKD Stage 5' in condition or 'Dialysis' in condition:
            creatinine = np.random.uniform(5.0, 12.0)
            gfr = np.random.uniform(5, 14)
            potassium += 1.5
            urea += 60
            hgb -= 5
            fluid = np.random.uniform(500, 1500) # Restricted for ESRD
        elif 'AKI' in condition:
            creatinine = np.random.uniform(2.0, 6.0) # Sudden rise
            potassium += 1.0
            urea += 50
        elif 'Diabetic' in condition:
            sugar = np.random.uniform(150, 300)
            creatinine += 0.5
        elif 'Hypertensive' in condition:
            creatinine += 0.3
            
        gfr = np.random.uniform(10, 100) if 'gfr' not in locals() else gfr
        
        # Determine Risk Level
        score = 0
        if potassium > 5.5 or potassium < 3.2: score += 4
        if creatinine > 5.0: score += 3
        if urea > 100: score += 2
        if hgb < 9.0: score += 2
        if condition in ['CKD Stage 5 (ESRD)', 'AKI (Acute Kidney Injury)']: score += 2
        
        risk_level = 'High' if score >= 6 else ('Moderate' if score >= 3 else 'Safe')
        
        records.append({
            'patient_id': i,
            'age': age,
            'condition_type': condition,
            'potassium': round(potassium, 2),
            'sodium': round(sodium, 2),
            'urea': round(urea, 1),
            'creatinine': round(creatinine, 2),
            'sugar': round(sugar, 1),
            'hgb': round(hgb, 1),
            'fluid': round(fluid, 0),
            'gfr': round(gfr, 1),
            'risk_level': risk_level
        })
        
    df = pd.DataFrame(records)
    
    # Ensure data directory exists
    if not os.path.exists('data'):
        os.makedirs('data')
        
    df.to_csv('data/dialysis_dataset_enhanced.csv', index=False)
    print(f"Generated {num_records} enhanced kidney patient records.")
    return df

if __name__ == "__main__":
    generate_enhanced_kidney_data(1200)
