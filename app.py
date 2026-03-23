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
        
        # Features must be in the same order as trained: ['potassium', 'sodium', 'urea', 'creatinine', 'sugar', 'hgb', 'fluid', 'gfr']
        features = [[potassium, sodium, urea, creatinine, sugar, hgb, fluid, gfr]]
        prediction = model.predict(features)
        return prediction[0]
    except Exception as e:
        print(f"Prediction error: {e}")
        return "Unknown"

# Routes
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
        foods_by_category = {}
        for category in df['category'].unique():
            category_foods = df[df['category'] == category].to_dict('records')
            for f in category_foods:
                rec = f['recommendation'].lower()
                if rec == 'safe': f['color'] = 'success'
                elif rec == 'limited': f['color'] = 'warning'
                else: f['color'] = 'error'
            foods_by_category[category] = category_foods
    return render_template('food.html', categorized_foods=foods_by_category)

@app.route('/diet-plan')
def diet_plan():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    import json

    nutrition_cols = ['calories', 'protein', 'potassium', 'sodium', 'phosphorus', 'fluid', 'unit']
    default_nutrition = {'calories': 0, 'protein': 0, 'potassium': 0, 'sodium': 0, 'phosphorus': 0, 'fluid': 0, 'unit': 'g'}

    if not os.path.exists('data/food_dataset.csv'):
        all_foods = []
        all_categories = []
    else:
        df = pd.read_csv('data/food_dataset.csv')
        # Fill missing nutritional columns with 0/defaults
        for col in nutrition_cols[:-1]:  # skip 'unit'
            if col not in df.columns:
                df[col] = 0
        if 'unit' not in df.columns:
            df['unit'] = 'g'
        df = df.fillna(0)

        all_foods = []
        for _, row in df.iterrows():
            food_entry = {
                'food_name':     str(row.get('food_name', '')),
                'category':      str(row.get('category', '')),
                'recommendation':str(row.get('recommendation', 'Safe')),
                'image_url':     str(row.get('image_url', '/static/images/food-placeholder.png')),
                'calories':      float(row.get('calories', 0)),
                'protein':       float(row.get('protein', 0)),
                'potassium':     float(row.get('potassium', 0)),
                'sodium':        float(row.get('sodium', 0)),
                'phosphorus':    float(row.get('phosphorus', 0)),
                'fluid':         float(row.get('fluid', 0)),
                'unit':          str(row.get('unit', 'g')),
            }
            all_foods.append(food_entry)

        all_categories = sorted(df['category'].dropna().unique().tolist())

    return render_template(
        'diet_plan.html',
        all_foods=all_foods,
        all_categories=all_categories,
        foods_json=all_foods
    )

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

    return render_template('dashboard.html', user=user, latest_record=latest_record, history=history, trends=trend_summary)

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

@app.route('/anime-dashboard')
def anime_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('anime_dashboard.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').lower()
    reply = ""
    
    # Advanced logic bridging patient context if logged in
    user_context = ""
    if 'user_id' in session:
        user = Patient.query.get(session['user_id'])
        if user:
            history = HealthRecord.query.filter_by(patient_id=user.id).order_by(HealthRecord.date.desc()).first()
            if history:
                user_context = f" Patient Data - K: {history.potassium}, Na: {history.sodium}, Risk: {history.risk_score}"

    # Rule-Based Engine (Fallback from LLM)
    if "banana" in user_message:
        reply = "❌ **Banana is high in potassium.** Avoid it. Try apple or grapes instead."
    elif "apple" in user_message:
        reply = "✅ **Apple is safe!** Great choice for your kidney diet."
    elif "potassium" in user_message and any(x in user_message for x in ["6.", "high", "danger", "my potassium is"]):
        reply = "⚠️ **High risk!** Your potassium level indicates danger. Avoid high potassium foods immediately and consult your doctor."
    elif "sodium" in user_message or "report" in user_message:
        reply = "Based on standard kidney diets, your sodium is a critical factor. Reduce salt intake to stay within safe bounds."
    elif "diet" in user_message or "safe food" in user_message:
        reply = "For your safety, stick to low-potassium foods like apples, cabbage, and white bread. Drink fluids strictly as prescribed."
    elif any(word in user_message for word in ["hi", "hello", "hey"]):
        reply = "Hello! I am DialyBot 🤖. How can I help you with your health or diet today?"
    else:
        reply = "I'm DialyBot! For complex queries, please consult your doctor. But feel free to ask me if a specific food (like banana or apple) is safe!"

    # Append personalized context if relevant
    if user_context and ("my" in user_message or "report" in user_message or "risk" in user_message):
        reply += f"\n\n*(Note: Your recent record shows {user_context.strip()})*"

    # Try LLM if available
    try:
        import openai
        if hasattr(openai, "api_key") and openai.api_key and openai.api_key != "YOUR_API_KEY":
            sys_message = "You are a dialysis diet assistant. Suggest safe foods and warn about risks."
            if user_context:
                sys_message += f"\nHere is the user's latest data: {user_context}"
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": sys_message},
                    {"role": "user", "content": user_message}
                ]
            )
            reply = response['choices'][0]['message']['content']
    except Exception:
        pass
        
    return {"reply": reply}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        train_model()
    app.run(debug=True)
