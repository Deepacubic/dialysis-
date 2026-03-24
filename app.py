from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import numpy as np
import os
from sklearn.tree import DecisionTreeClassifier
import pickle
from translations import translations

app = Flask(__name__)
app.secret_key = 'dialycare_secret_key'

# Database Configuration (SQLite)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    weight = db.Column(db.Float)
    dialysis_type = db.Column(db.String(50))
    kidney_condition = db.Column(db.String(100))
    ckd_stage = db.Column(db.String(50))

class HealthRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    potassium = db.Column(db.Float)
    sodium = db.Column(db.Float)
    fluid_intake = db.Column(db.Float)
    weight = db.Column(db.Float)
    bp_sys = db.Column(db.Integer)
    bp_dia = db.Column(db.Integer)
    # New Medical Parameters
    urea = db.Column(db.Float)
    platelets = db.Column(db.Float)
    chloride = db.Column(db.Float)
    creatinine = db.Column(db.Float)
    cholesterol = db.Column(db.Float)
    iron = db.Column(db.Float)
    calcium = db.Column(db.Float)
    bilirubin = db.Column(db.Float)
    sugar = db.Column(db.Float)
    hcv_status = db.Column(db.String(20)) # Positive/Negative
    wbc = db.Column(db.Float)
    rbc = db.Column(db.Float)
    hgb = db.Column(db.Float)
    gfr = db.Column(db.Float)
    risk_score = db.Column(db.String(20))

# AI Model Integration
def train_model():
    dataset_path = 'data/dialysis_dataset_enhanced.csv'
    if not os.path.exists(dataset_path):
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
    return model

def predict_risk(potassium, sodium, fluid, urea=40.0, creatinine=1.2, sugar=100.0, hgb=12.0, gfr=90.0):
    try:
        if not os.path.exists('model.pkl'):
            model = train_model()
        else:
            with open('model.pkl', 'rb') as f:
                model = pickle.load(f)
        
        # Features must be in the same order as trained
        features = [[potassium, sodium, urea, creatinine, sugar, hgb, fluid, gfr]]
        prediction = model.predict(features)
        return prediction[0]
    except Exception as e:
        print(f"Prediction error: {e}")
        return "Unknown"

# --- Database Seeding ---
def seed_database():
    if not Patient.query.first():
        hashed_pw = 'password'  # In production, use hashed passwords!
        test_patient = Patient(
            name='Test User',
            email='test@example.com',
            password=hashed_pw
        )
        db.session.add(test_patient)
        db.session.commit()
        
        # Create a sample health record for the test user
        test_record = HealthRecord(
            patient_id=test_patient.id,
            potassium=4.5,
            sodium=138.0,
            fluid_intake=1200.0,
            weight=70.5,
            bp_sys=120,
            bp_dia=80,
            urea=45.0,
            creatinine=1.8,
            sugar=110.0,
            hgb=11.5,
            gfr=58.0,
            risk_score='Low'
        )
        db.session.add(test_record)
        db.session.commit()

# --- Initialization block for Gunicorn / Render ---
with app.app_context():
    db.create_all()
    seed_database()
    if not os.path.exists('model.pkl'):
        train_model()

# Routes
@app.route('/health')
def health_check():
    return "OK", 200

@app.route('/')
def home():
    return render_template('index.html')

@app.context_processor
def inject_translate():
    lang = session.get('lang', 'en')
    def translate(key):
        return translations.get(lang, translations['en']).get(key, key)
    return dict(_=translate, current_lang=lang)

def tr(key):
    lang = session.get('lang', 'en')
    return translations.get(lang, translations['en']).get(key, key)

@app.route('/set-language/<lang>')
def set_language(lang):
    if lang in translations:
        session['lang'] = lang
    return redirect(request.referrer or url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = Patient.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash(tr('login_success'), 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(tr('login_invalid'), 'error')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        age = request.form.get('age')
        dialysis_type = request.form.get('dialysis_type')
        
        # Check if user already exists
        existing_user = Patient.query.filter_by(email=email).first()
        if existing_user:
            flash(tr('email_exists'), 'error')
            return redirect(url_for('register'))
            
        new_user = Patient(
            name=name, 
            email=email, 
            password=password, 
            age=int(age) if age else None, 
            dialysis_type=dialysis_type,
            kidney_condition=request.form.get('kidney_condition'),
            ckd_stage=request.form.get('ckd_stage')
        )
        db.session.add(new_user)
        db.session.commit()
        flash(tr('register_success'), 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/food')
def food():
    if not os.path.exists('data/food_dataset.csv'):
        foods_by_category = {}
    else:
        df = pd.read_csv('data/food_dataset.csv')
        df = df.fillna(0)
        
        def clean_val(v):
            return str(v).strip()

        # SUPER-CLEANING logic: Only keep categories and food names that are real text
        def is_real_text(s):
            s = clean_val(s)
            if not s or s == "0" or s == "nan" or len(s) < 2: return False
            if s.replace('.','',1).isdigit(): return False # rejects "0", "15", "0.0" etc
            return True

        foods_by_category = {}
        
        def get_food_side_effects(row):
            effects = []
            if float(row.get('potassium', 0)) > 200:
                effects.append('High Potassium (Risk of Arrhythmia)')
            if float(row.get('sodium', 0)) > 140:
                effects.append('High Sodium (Risk of High BP/Edema)')
            if float(row.get('phosphorus', 0)) > 150:
                effects.append('High Phosphorus (Bone disease risk)')
            
            rec = str(row.get('recommendation', '')).lower()
            if rec == 'safe':
                return 'Generally safe' if not effects else ', '.join(effects)
            if not effects:
                return 'Adverse effects on kidneys in large quantities'
            return ', '.join(effects)

        # Categorize
        for category in df['category'].dropna().unique():
            cat_str = clean_val(category)
            if not is_real_text(cat_str): continue
            
            category_foods = df[df['category'] == category].to_dict('records')
            valid_foods = []
            for f in category_foods:
                fname = clean_val(f.get('food_name', ''))
                if is_real_text(fname):
                    rec = str(f.get('recommendation', '')).lower()
                    if rec == 'safe': f['color'] = 'success'
                    elif rec == 'limited': f['color'] = 'warning'
                    else: f['color'] = 'error'
                    f['side_effects'] = get_food_side_effects(f)
                    valid_foods.append(f)
            
            if valid_foods:
                foods_by_category[cat_str] = valid_foods

    return render_template('food.html', categorized_foods=foods_by_category)

@app.route('/diet-plan')
def diet_plan():
    # Public route - personalized if logged in, general tool if guest
    user = None
    last_record = None
    if 'user_id' in session:
        user = Patient.query.get(session['user_id'])
        if user:
            last_record = HealthRecord.query.filter_by(patient_id=user.id).order_by(HealthRecord.date.desc()).first()

    nutrition_cols = ['calories', 'protein', 'potassium', 'sodium', 'phosphorus', 'fluid', 'unit']
    
    if not os.path.exists('data/food_dataset.csv'):
        all_foods = []
        all_categories = []
    else:
        df = pd.read_csv('data/food_dataset.csv')
        df = df.fillna(0)
        
        def clean_val(v):
            return str(v).strip()

        def is_real_text(s):
            s = clean_val(s)
            if not s or s == "0" or s == "nan" or len(s) < 2: return False
            if s.replace('.','',1).isdigit(): return False
            return True

        def get_food_side_effects(row):
            effects = []
            if float(row.get('potassium', 0)) > 200:
                effects.append('High Potassium (Risk of Arrhythmia)')
            if float(row.get('sodium', 0)) > 140:
                effects.append('High Sodium (Risk of High BP/Edema)')
            if float(row.get('phosphorus', 0)) > 150:
                effects.append('High Phosphorus (Bone disease risk)')
            rec = str(row.get('recommendation', '')).lower()
            if rec == 'safe':
                return 'Generally safe' if not effects else ', '.join(effects)
            if not effects:
                return 'Adverse effects on kidneys in large quantities'
            return ', '.join(effects)

        all_foods = []
        for _, row in df.iterrows():
            name = clean_val(row.get('food_name', ''))
            cat = clean_val(row.get('category', ''))
            
            if not is_real_text(name) or not is_real_text(cat):
                continue
                
            food_entry = {
                'food_name':     name,
                'category':      cat,
                'recommendation':str(row.get('recommendation', 'Safe')),
                'image_url':     str(row.get('image_url', '/static/images/food-placeholder.png')),
                'calories':      float(row.get('calories', 0)),
                'protein':       float(row.get('protein', 0)),
                'potassium':     float(row.get('potassium', 0)),
                'sodium':        float(row.get('sodium', 0)),
                'phosphorus':    float(row.get('phosphorus', 0)),
                'fluid':         float(row.get('fluid', 0)),
                'unit':          str(row.get('unit', 'g')),
                'side_effects':  get_food_side_effects(row)
            }
            all_foods.append(food_entry)

        all_categories = sorted(list(set([f['category'] for f in all_foods])))

    return render_template('diet_plan.html', all_foods=all_foods, all_categories=all_categories, user=user, last_record=last_record)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = Patient.query.get(session['user_id'])
    # Get all records for history
    history = HealthRecord.query.filter_by(patient_id=user.id).order_by(HealthRecord.date.desc()).all()
    # Get latest health record if exists
    latest_record = history[0] if history else None
    
    # AI Trend Analysis
    trend_summary = []
    if len(history) >= 2:
        latest = history[0]
        previous = history[1]
        
        # Creatinine Trend
        if latest.creatinine > previous.creatinine * 1.1:
            trend_summary.append({'metric': 'creatinine', 'status': 'Worsening', 'message': tr('trend_creatinine_up'), 'color': 'error'})
        elif latest.creatinine < previous.creatinine * 0.9:
            trend_summary.append({'metric': 'creatinine', 'status': 'Improving', 'message': tr('trend_creatinine_down'), 'color': 'success'})
        else:
            trend_summary.append({'metric': 'creatinine', 'status': 'Stable', 'message': tr('trend_creatinine_stable'), 'color': 'info'})
            
        # eGFR Trend
        if latest.gfr and previous.gfr:
            if latest.gfr < previous.gfr * 0.9:
                trend_summary.append({'metric': 'egfr', 'status': 'Decreasing', 'message': tr('trend_gfr_down'), 'color': 'error'})
            elif latest.gfr > previous.gfr * 1.1:
                trend_summary.append({'metric': 'egfr', 'status': 'Increasing', 'message': tr('trend_gfr_up'), 'color': 'success'})
        
        # Potassium Trend
        if latest.potassium > 5.5:
            trend_summary.append({'metric': 'potassium', 'status': 'High', 'message': tr('trend_potassium_high'), 'color': 'error'})
        elif latest.potassium < 3.5:
            trend_summary.append({'metric': 'potassium', 'status': 'Low', 'message': tr('trend_potassium_low'), 'color': 'warning'})
        else:
            trend_summary.append({'metric': 'potassium', 'status': 'Normal', 'message': tr('trend_potassium_normal'), 'color': 'success'})

    # Enhanced Intelligent Dietary Guidance System
    dietary_tips = []
    food_guidance = []
    
    if latest_record:
        risk_lower = latest_record.risk_score.lower()
        if "high" in risk_lower:
            dietary_tips = ["Avoid high potassium foods like banana, orange", "Reduce salt intake", "Limit fluid intake to prescribed level", "Eat more low potassium foods like apple, cabbage"]
        elif "moderate" in risk_lower or "medium" in risk_lower:
            dietary_tips = ["Limit high sodium foods", "Drink controlled water", "Maintain balanced diet and regular tracking"]
        else:
            dietary_tips = ["Maintain current diet", "Follow regular monitoring", "Stay hydrated appropriately"]
            
        if latest_record.potassium > 5.5:
            food_guidance.append({"name": "Banana", "status": "Avoid", "reason": "High potassium", "color": "danger"})
            food_guidance.append({"name": "Orange", "status": "Avoid", "reason": "High potassium", "color": "danger"})
        else:
            food_guidance.append({"name": "Apple", "status": "Safe", "reason": "Low potassium", "color": "safe"})
            food_guidance.append({"name": "Rice", "status": "Safe", "reason": "Low sodium", "color": "safe"})
            
        if latest_record.sodium > 150:
            food_guidance.append({"name": "Pickle", "status": "Avoid", "reason": "Extremely high sodium", "color": "danger"})
            food_guidance.append({"name": "Salted snacks", "status": "Avoid", "reason": "High sodium content", "color": "danger"})
        else:
            food_guidance.append({"name": "Fresh Vegetables", "status": "Safe", "reason": "Natural low sodium", "color": "safe"})
            food_guidance.append({"name": "Milk", "status": "Limited", "reason": "Moderate potassium", "color": "warning"})

    return render_template('dashboard.html', user=user, latest_record=latest_record, history=history, trends=trend_summary, dietary_tips=dietary_tips, food_guidance=food_guidance)

@app.route('/health-entry', methods=['GET', 'POST'])
def health_entry():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user = Patient.query.get(session['user_id'])
        age = user.age or 52
        
        # AI Prediction Data
        potassium = float(request.form.get('potassium'))
        sodium = float(request.form.get('sodium'))
        fluid = float(request.form.get('fluid'))
        creatinine = float(request.form.get('creatinine'))
        urea = float(request.form.get('urea'))
        sugar = float(request.form.get('sugar'))
        hgb = float(request.form.get('hgb'))
        
        # Calculate eGFR (Simplified MDRD)
        gfr = round(175 * (creatinine**-1.154) * (age**-0.203), 1)
        
        # New Medical Data
        data = {
            'patient_id': session['user_id'],
            'potassium': potassium,
            'sodium': sodium,
            'fluid_intake': fluid,
            'weight': float(request.form.get('weight')),
            'bp_sys': int(request.form.get('bp_sys')),
            'bp_dia': int(request.form.get('bp_dia')),
            'urea': urea,
            'platelets': float(request.form.get('platelets')),
            'chloride': float(request.form.get('chloride')),
            'creatinine': creatinine,
            'cholesterol': float(request.form.get('cholesterol')),
            'iron': float(request.form.get('iron')),
            'calcium': float(request.form.get('calcium')),
            'bilirubin': float(request.form.get('bilirubin')),
            'sugar': sugar,
            'hcv_status': request.form.get('hcv_status'),
            'wbc': float(request.form.get('wbc')),
            'rbc': float(request.form.get('rbc')),
            'hgb': hgb,
            'gfr': gfr,
            'risk_score': predict_risk(
                potassium, 
                sodium, 
                fluid, 
                urea=urea, 
                creatinine=creatinine,
                sugar=sugar,
                hgb=hgb,
                gfr=gfr
            )
        }
        
        new_record = HealthRecord(**data)
        db.session.add(new_record)
        db.session.commit()
        
        flash(f'Comprehensive record added! Risk Level: {data["risk_score"]}', 'info')
        return redirect(url_for('dashboard'))
        
    return render_template('health_entry.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = Patient.query.get(session['user_id'])
    # Get all records for history
    history = HealthRecord.query.filter_by(patient_id=user.id).order_by(HealthRecord.date.desc()).all()
    # Get latest health record if exists
    latest_record = history[0] if history else None
    
    # AI Trend Analysis
    trend_summary = []
    if len(history) >= 2:
        latest = history[0]
        previous = history[1]
        
        # Creatinine Trend
        if latest.creatinine > previous.creatinine * 1.1:
            trend_summary.append({'metric': 'creatinine', 'status': 'Worsening', 'message': tr('trend_creatinine_up'), 'color': 'error'})
        elif latest.creatinine < previous.creatinine * 0.9:
            trend_summary.append({'metric': 'creatinine', 'status': 'Improving', 'message': tr('trend_creatinine_down'), 'color': 'success'})
        else:
            trend_summary.append({'metric': 'creatinine', 'status': 'Stable', 'message': tr('trend_creatinine_stable'), 'color': 'info'})
            
        # eGFR Trend
        if latest.gfr and previous.gfr:
            if latest.gfr < previous.gfr * 0.9:
                trend_summary.append({'metric': 'egfr', 'status': 'Decreasing', 'message': tr('trend_gfr_down'), 'color': 'error'})
            elif latest.gfr > previous.gfr * 1.1:
                trend_summary.append({'metric': 'egfr', 'status': 'Increasing', 'message': tr('trend_gfr_up'), 'color': 'success'})
        
        # Potassium Trend
        if latest.potassium > 5.5:
            trend_summary.append({'metric': 'potassium', 'status': 'High', 'message': tr('trend_potassium_high'), 'color': 'error'})
        elif latest.potassium < 3.5:
            trend_summary.append({'metric': 'potassium', 'status': 'Low', 'message': tr('trend_potassium_low'), 'color': 'warning'})
        else:
            trend_summary.append({'metric': 'potassium', 'status': 'Normal', 'message': tr('trend_potassium_normal'), 'color': 'success'})

    # Enhanced Intelligent Dietary Guidance System
    dietary_tips = []
    food_guidance = []
    
    if latest_record:
        risk_lower = latest_record.risk_score.lower()
        if "high" in risk_lower:
            dietary_tips = ["Avoid high potassium foods like banana, orange", "Reduce salt intake", "Limit fluid intake to prescribed level", "Eat more low potassium foods like apple, cabbage"]
        elif "moderate" in risk_lower or "medium" in risk_lower:
            dietary_tips = ["Limit high sodium foods", "Drink controlled water", "Maintain balanced diet and regular tracking"]
        else:
            dietary_tips = ["Maintain current diet", "Follow regular monitoring", "Stay hydrated appropriately"]
            
        if latest_record.potassium > 5.5:
            food_guidance.append({"name": "Banana", "status": "Avoid", "reason": "High potassium", "color": "danger"})
            food_guidance.append({"name": "Orange", "status": "Avoid", "reason": "High potassium", "color": "danger"})
        else:
            food_guidance.append({"name": "Apple", "status": "Safe", "reason": "Low potassium", "color": "safe"})
            food_guidance.append({"name": "Rice", "status": "Safe", "reason": "Low sodium", "color": "safe"})
            
        if latest_record.sodium > 150:
            food_guidance.append({"name": "Pickle", "status": "Avoid", "reason": "Extremely high sodium", "color": "danger"})
            food_guidance.append({"name": "Salted snacks", "status": "Avoid", "reason": "High sodium content", "color": "danger"})
        else:
            food_guidance.append({"name": "Fresh Vegetables", "status": "Safe", "reason": "Natural low sodium", "color": "safe"})
            food_guidance.append({"name": "Milk", "status": "Limited", "reason": "Moderate potassium", "color": "warning"})

    return render_template('dashboard.html', user=user, latest_record=latest_record, history=history, trends=trend_summary, dietary_tips=dietary_tips, food_guidance=food_guidance)

@app.route('/health-entry', methods=['GET', 'POST'])
def health_entry():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user = Patient.query.get(session['user_id'])
        age = user.age or 52
        
        # AI Prediction Data
        potassium = float(request.form.get('potassium'))
        sodium = float(request.form.get('sodium'))
        fluid = float(request.form.get('fluid'))
        creatinine = float(request.form.get('creatinine'))
        urea = float(request.form.get('urea'))
        sugar = float(request.form.get('sugar'))
        hgb = float(request.form.get('hgb'))
        
        # Calculate eGFR (Simplified MDRD)
        gfr = round(175 * (creatinine**-1.154) * (age**-0.203), 1)
        
        # New Medical Data
        data = {
            'patient_id': session['user_id'],
            'potassium': potassium,
            'sodium': sodium,
            'fluid_intake': fluid,
            'weight': float(request.form.get('weight')),
            'bp_sys': int(request.form.get('bp_sys')),
            'bp_dia': int(request.form.get('bp_dia')),
            'urea': urea,
            'platelets': float(request.form.get('platelets')),
            'chloride': float(request.form.get('chloride')),
            'creatinine': creatinine,
            'cholesterol': float(request.form.get('cholesterol')),
            'iron': float(request.form.get('iron')),
            'calcium': float(request.form.get('calcium')),
            'bilirubin': float(request.form.get('bilirubin')),
            'sugar': sugar,
            'hcv_status': request.form.get('hcv_status'),
            'wbc': float(request.form.get('wbc')),
            'rbc': float(request.form.get('rbc')),
            'hgb': hgb,
            'gfr': gfr,
            'risk_score': predict_risk(
                potassium, 
                sodium, 
                fluid, 
                urea=urea, 
                creatinine=creatinine,
                sugar=sugar,
                hgb=hgb,
                gfr=gfr
            )
        }
        
        new_record = HealthRecord(**data)
        db.session.add(new_record)
        db.session.commit()
        
        flash(f'Comprehensive record added! Risk Level: {data["risk_score"]}', 'info')
        return redirect(url_for('dashboard'))
        
    return render_template('health_entry.html')


@app.route('/diet-plan')
def diet_plan():
    # Public route - personalized if logged in, general tool if guest
    user = None
    last_record = None
    if 'user_id' in session:
        user = Patient.query.get(session['user_id'])
        if user:
            last_record = HealthRecord.query.filter_by(patient_id=user.id).order_by(HealthRecord.date.desc()).first()

    if not os.path.exists('data/food_dataset.csv'):
        all_foods = []
        all_categories = []
    else:
        df = pd.read_csv('data/food_dataset.csv')
        df = df.fillna(0)
        
        def clean_val(v):
            return str(v).strip()

        def is_real_text(s):
            s = clean_val(s)
            if not s or s == "0" or s == "nan" or len(s) < 2: return False
            if s.replace('.','',1).isdigit(): return False
            return True

        def get_food_side_effects(row):
            effects = []
            if float(row.get('potassium', 0)) > 200:
                effects.append('High Potassium (Risk of Arrhythmia)')
            if float(row.get('sodium', 0)) > 140:
                effects.append('High Sodium (Risk of High BP/Edema)')
            if float(row.get('phosphorus', 0)) > 150:
                effects.append('High Phosphorus (Bone disease risk)')
            rec = str(row.get('recommendation', '')).lower()
            if rec == 'safe':
                return 'Generally safe' if not effects else ', '.join(effects)
            if not effects:
                return 'Adverse effects on kidneys in large quantities'
            return ', '.join(effects)

        all_foods = []
        for _, row in df.iterrows():
            name = clean_val(row.get('food_name', ''))
            cat = clean_val(row.get('category', ''))
            
            if not is_real_text(name) or not is_real_text(cat):
                continue
                
            food_entry = {
                'food_name':     name,
                'category':      cat,
                'recommendation':str(row.get('recommendation', 'Safe')),
                'image_url':     str(row.get('image_url', '/static/images/food-placeholder.png')),
                'calories':      float(row.get('calories', 0)),
                'protein':       float(row.get('protein', 0)),
                'potassium':     float(row.get('potassium', 0)),
                'sodium':        float(row.get('sodium', 0)),
                'phosphorus':    float(row.get('phosphorus', 0)),
                'fluid':         float(row.get('fluid', 0)),
                'unit':          str(row.get('unit', 'g')),
                'side_effects':  get_food_side_effects(row)
            }
            all_foods.append(food_entry)

        all_categories = sorted(list(set([f['category'] for f in all_foods])))

    return render_template('diet_plan.html', all_foods=all_foods, all_categories=all_categories, user=user, last_record=last_record)

@app.route('/anime-dashboard')
def anime_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('anime_dashboard.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').strip()
    if not user_message:
        return {"reply": "Please ask me something!"}
        
    low_message = user_message.lower()
    
    # 1. Fetch Patient Context
    patient_context_str = ""
    history = None
    if 'user_id' in session:
        user = Patient.query.get(session['user_id'])
        if user:
            history = HealthRecord.query.filter_by(patient_id=user.id).order_by(HealthRecord.date.desc()).first()
            if history:
                patient_context_str = f"(Patient: {user.name}, K: {history.potassium}, Na: {history.sodium}, GFR: {history.gfr}, Urea: {history.urea}, Creatinine: {history.creatinine}, Risk: {history.risk_score})"

    # 2. Multi-Domain Logic Engine
    reply = ""
    
    # --- DOMAIN: Report Analyzer ---
    if any(word in low_message for word in ["report", "analyze", "explain", "result", "my data"]):
        if not history:
            reply = "I don't see any lab reports in your file yet! 📁 Please use the **Health Entry** page to log your data first."
        else:
            status = "Low Risk" if history.risk_score < 40 else "Moderate Risk" if history.risk_score < 70 else "High Risk"
            reply = f"""📊 **Your Lab Report Summary:**
- **Status:** {status} ({history.risk_score}/100)
- **Creatinine:** {history.creatinine} mg/dL (Indicates kidney filtration)
- **Urea:** {history.urea} mg/dL (Indicates protein waste levels)
- **BP:** {history.bp_sys}/{history.bp_dia} mmHg
- **Advice:** {"Your values look stable. Stick to current diet." if history.risk_score < 50 else "⚠️ Warning: Your waste levels are elevating. Please restrict fluids and skip high-protein meals."}"""

    # --- DOMAIN: Diet Assistant ---
    elif any(word in low_message for word in ["banana", "apple", "potato", "eat", "food", "diet", "drink"]):
        if "banana" in low_message:
            reply = "❌ **Banana** is high in potassium (358mg/100g). For a dialysis patient, this can trigger arrhythmia. **Avoid it.** Try grapes instead!"
        elif "apple" in low_message:
            reply = "✅ **Apple** is a perfect low-potassium choice. Safe to eat!"
        elif "potato" in low_message:
            reply = "⚠️ **Potato** is high in potassium. If you eat it, soak sliced potatoes in water for 2 hours (leaching) to remove some potassium."
        elif "water" in low_message or "fluid" in low_message:
            limit = history.fluid_intake if history else 1000 # Corrected from history.fluid to history.fluid_intake
            reply = f"💧 **Fluid Management:** Based on your needs, keep fluid intake below **{limit}ml/day**. This includes water, tea, and soups."
        else:
            reply = "🍽️ Use the **Diet Plan** tool to build your meal! I recommend Low-Sodium and Low-Potassium foods for your condition."

    # --- DOMAIN: General/Risk ---
    elif any(word in low_message for word in ["risk", "danger", "potassium", "sodium"]):
        if history and history.potassium > 5.5:
             reply = f"⚠️ **CRITICAL ALERT:** Your potassium is {history.potassium}. This is dangerous for your heart rhythm. **Avoid ALL fruits except apples/grapes.**"
        else:
             reply = "Kidney health depends on 3 pillars: Low Potassium, Low Sodium, and Fluid Control. Stay in the 'Safe' zone of my charts!"

    # --- DOMAIN: Hello/Help ---
    elif any(word in low_message for word in ["hi", "hello", "hey", "help"]):
        reply = "Hello! I am **DialyBot AI 🤖**, your Multi-Domain assistant. I can:\n\n1. 📊 **Explain your Reports**\n2. 🍽️ **Suggest Safe Foods**\n3. ⚠️ **Give Risk Alerts**\n\nWhat would you like to know?"
    else:
        reply = "I'm DialyBot! I can help with diet or health data. Try asking: *'Explain my report'* or *'Can I eat potatoes?'*"

    # 3. LLM Priority (If enabled)
    try:
        import openai
        import os
        api_key = os.environ.get("OPENAI_API_KEY") or (hasattr(openai, "api_key") and openai.api_key and openai.api_key != "YOUR_API_KEY")
        if api_key:
            system_prompt = f"""
            You are 'DialyBot', a Multi-Domain Medical AI for Dialysis.
            Patient Data Context: {patient_context_str if patient_context_str else 'Public Guest'}
            Domains: [Diet Assistant, Lab Report Explainer, Risk Alert, Health Tips].
            Rules:
            - If user's Potassium or Sodium in context is High, start with a warning.
            - Potassium limit: <2000mg. Sodium: <2000mg. Fluid: <1000ml.
            - Keep replies professional and empathetic.
            - Mention specific lab values if explaining report.
            """
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
                max_tokens=250
            )
            reply = response['choices'][0]['message']['content']
    except Exception as e:
        print(f"LLM Error: {e}")

    return {"reply": reply}

@app.route('/health')
def health():
    return "OK"

# End of file logic below. Global init already handles seeding.

if __name__ == '__main__':
    # When running locally, already initialized globally
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
