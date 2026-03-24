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
    urea = db.Column(db.Float)
    platelets = db.Column(db.Float)
    chloride = db.Column(db.Float)
    creatinine = db.Column(db.Float)
    cholesterol = db.Column(db.Float)
    iron = db.Column(db.Float)
    calcium = db.Column(db.Float)
    bilirubin = db.Column(db.Float)
    sugar = db.Column(db.Float)
    hcv_status = db.Column(db.String(20))
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
        features = [[potassium, sodium, urea, creatinine, sugar, hgb, fluid, gfr]]
        prediction = model.predict(features)
        return prediction[0]
    except Exception as e:
        print(f"Prediction error: {e}")
        return "Unknown"

# --- Common Logic ---
@app.context_processor
def inject_translate():
    def translate(key):
        lang = session.get('lang', 'en')
        return translations.get(lang, translations['en']).get(key, key)
    return dict(_=translate, tr=translate)

def tr(key):
    lang = session.get('lang', 'en')
    return translations.get(lang, translations['en']).get(key, key)

# --- Routes ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/set-language/<lang>')
def set_language(lang):
    if lang in ['en', 'ta']:
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
            flash(tr('login_success'), 'success')
            return redirect(url_for('dashboard'))
        flash(tr('login_error'), 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        if Patient.query.filter_by(email=email).first():
            flash('Email already exists!', 'error')
            return redirect(url_for('register'))
        new_user = Patient(
            name=request.form.get('name'),
            email=email,
            password=request.form.get('password'),
            age=int(request.form.get('age', 52)),
            gender=request.form.get('gender'),
            dialysis_type=request.form.get('dialysis_type'),
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
        def clean_val(v): return str(v).strip()
        def is_real_text(s):
            s = clean_val(s)
            if not s or s == "0" or s == "nan" or len(s) < 2: return False
            if s.replace('.','',1).isdigit(): return False
            return True
        foods_by_category = {}
        for category in df['category'].dropna().unique():
            cat_str = clean_val(category)
            if not is_real_text(cat_str): continue
            category_foods = df[df['category'] == category].to_dict('records')
            valid_foods = []
            for f in category_foods:
                if is_real_text(clean_val(f.get('food_name', ''))):
                    valid_foods.append(f)
            if valid_foods: foods_by_category[cat_str] = valid_foods
    return render_template('food.html', categorized_foods=foods_by_category)

@app.route('/diet-plan')
def diet_plan():
    user = None
    last_record = None
    if 'user_id' in session:
        user = Patient.query.get(session['user_id'])
        if user:
            last_record = HealthRecord.query.filter_by(patient_id=user.id).order_by(HealthRecord.date.desc()).first()
    all_foods = []
    all_categories = []
    if os.path.exists('data/food_dataset.csv'):
        df = pd.read_csv('data/food_dataset.csv').fillna(0)
        def clean_val(v): return str(v).strip()
        def is_real_text(s):
            s = clean_val(s)
            return bool(s and s != "0" and s != "nan" and len(s) >= 2 and not s.replace('.','',1).isdigit())
        for _, row in df.iterrows():
            name = clean_val(row.get('food_name', ''))
            cat = clean_val(row.get('category', ''))
            if not is_real_text(name) or not is_real_text(cat): continue
            all_foods.append({
                'food_name': name, 'category': cat, 'recommendation': str(row.get('recommendation', 'Safe')),
                'image_url': str(row.get('image_url', '/static/images/food-placeholder.png')),
                'calories': float(row.get('calories', 0)), 'protein': float(row.get('protein', 0)),
                'potassium': float(row.get('potassium', 0)), 'sodium': float(row.get('sodium', 0)),
                'phosphorus': float(row.get('phosphorus', 0)), 'fluid': float(row.get('fluid', 0)),
                'unit': str(row.get('unit', 'g'))
            })
        all_categories = sorted(list(set([f['category'] for f in all_foods])))
    return render_template('diet_plan.html', all_foods=all_foods, all_categories=all_categories, user=user, last_record=last_record)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = Patient.query.get(session['user_id'])
    history = HealthRecord.query.filter_by(patient_id=user.id).order_by(HealthRecord.date.desc()).all()
    latest_record = history[0] if history else None
    
    trend_summary = []
    if len(history) >= 2:
        latest, prev = history[0], history[1]
        if latest.creatinine > prev.creatinine * 1.05: trend_summary.append({'metric': 'creatinine', 'status': 'Worsening', 'message': tr('trend_creatinine_up'), 'color': 'error'})
        elif latest.creatinine < prev.creatinine * 0.95: trend_summary.append({'metric': 'creatinine', 'status': 'Improving', 'message': tr('trend_creatinine_down'), 'color': 'success'})
        if latest.gfr and prev.gfr and latest.gfr < prev.gfr * 0.95: trend_summary.append({'metric': 'egfr', 'status': 'Decreasing', 'message': tr('trend_gfr_down'), 'color': 'error'})
    
    # Chart Data (last 7 entries)
    dates = []
    creatinine_values = []
    chart_history = history[:7][::-1]
    for rec in chart_history:
        dates.append(rec.date.strftime('%d %b'))
        creatinine_values.append(rec.creatinine)

    dietary_tips = []
    if latest_record:
        risk = latest_record.risk_score.lower()
        if "high" in risk: dietary_tips = ["Avoid high potassium foods like banana", "Reduce salt intake", "Limit fluids to 500ml-700ml"]
        elif "moderate" in risk: dietary_tips = ["Limit sodium to < 2g per day", "Control fluid intake", "Avoid processed foods"]
        else: dietary_tips = ["Maintain current kidney-friendly diet", "Monitor fluid intake daily", "Follow doctor's advice on activity"]
    
    return render_template('dashboard.html', 
                           user=user, 
                           latest_record=latest_record, 
                           history=history, 
                           trends=trend_summary, 
                           dates=dates, 
                           creatinine_values=creatinine_values,
                           dietary_tips=dietary_tips)

@app.route('/health-entry', methods=['GET', 'POST'])
def health_entry():
    if 'user_id' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        user = Patient.query.get(session['user_id'])
        age = user.age or 52
        potassium = float(request.form.get('potassium'))
        sodium = float(request.form.get('sodium'))
        fluid = float(request.form.get('fluid'))
        creatinine = float(request.form.get('creatinine'))
        urea = float(request.form.get('urea'))
        sugar = float(request.form.get('sugar'))
        hgb = float(request.form.get('hgb'))
        gfr = round(175 * (creatinine**-1.154) * (age**-0.203), 1)
        data = {
            'patient_id': user.id, 'potassium': potassium, 'sodium': sodium, 'fluid_intake': fluid,
            'weight': float(request.form.get('weight')), 'bp_sys': int(request.form.get('bp_sys')),
            'bp_dia': int(request.form.get('bp_dia')), 'urea': urea, 'platelets': float(request.form.get('platelets', 0)),
            'chloride': float(request.form.get('chloride', 0)), 'creatinine': creatinine,
            'cholesterol': float(request.form.get('cholesterol', 0)), 'iron': float(request.form.get('iron', 0)),
            'calcium': float(request.form.get('calcium', 0)), 'bilirubin': float(request.form.get('bilirubin', 0)),
            'sugar': sugar, 'hcv_status': request.form.get('hcv_status', 'Negative'),
            'wbc': float(request.form.get('wbc', 0)), 'rbc': float(request.form.get('rbc', 0)),
            'hgb': hgb, 'gfr': gfr,
            'risk_score': predict_risk(potassium, sodium, fluid, urea, creatinine, sugar, hgb, gfr)
        }
        db.session.add(HealthRecord(**data))
        db.session.commit()
        flash(f'Record added! Risk: {data["risk_score"]}', 'info')
        return redirect(url_for('dashboard'))
    return render_template('health_entry.html')

@app.route('/anime-dashboard')
def anime_dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('anime_dashboard.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '').strip().lower()
    if not user_msg: return {"reply": "How can I help you today?"}
    
    # 1. Fetch Context
    history = None
    if 'user_id' in session:
        history = HealthRecord.query.filter_by(patient_id=session['user_id']).order_by(HealthRecord.date.desc()).first()
    
    patient_context = f"(Patient Labs: Creatinine {history.creatinine if history else 'N/A'}, K {history.potassium if history else 'N/A'})"

    # 2. Rule-Based Fallback (Instant & Free)
    rule_reply = None
    if "banana" in user_msg: rule_reply = "❌ **Banana** is high in potassium. **Avoid it.** Try an apple!"
    elif "report" in user_msg and history:
        status = "Low Risk" if float(str(history.risk_score).replace('%','')) < 40 else "High Risk"
        rule_reply = f"📊 **Report Analyzer:** Status is {status}. Creatinine: {history.creatinine}. Visit Dashboard for full trends!"

    # 3. Multi-Provider LLM Engine (Open Source Focused)
    final_reply = rule_reply
    
    try:
        # A. Attempt OpenAI (GPT-3.5)
        import openai
        api_key = os.environ.get("OPENAI_API_KEY")
        if not final_reply and api_key and api_key != "YOUR_API_KEY":
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": f"You are DialyBot, a Dialysis AI. {patient_context}"}, {"role": "user", "content": user_msg}],
                max_tokens=150
            )
            final_reply = resp['choices'][0]['message']['content']

        # B. Attempt Hugging Face (Open Source Llama-3/Mistral)
        if not final_reply:
            import requests
            hf_token = os.environ.get("HUGGINGFACE_TOKEN") # High-performance Open Source LLM
            if hf_token:
                API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
                headers = {"Authorization": f"Bearer {hf_token}"}
                payload = {"inputs": f"Medical Assistant (Dialysis): User says: {user_msg}. Respond concisely as DialyBot."}
                hf_resp = requests.post(API_URL, headers=headers, json=payload)
                if hf_resp.status_code == 200:
                    final_reply = hf_resp.json()[0]['generated_text'].split("Respond concisely as DialyBot.")[-1].strip()
    except Exception as e:
        print(f"LLM Provider Error: {e}")

    # C. Default Response
    if not final_reply:
        final_reply = "I'm DialyBot! Try asking: 'Can I eat potato?' or 'Explain my health report'."

    return {"reply": final_reply}

@app.route('/clear-chat', methods=['POST'])
def clear_chat():
    # Simply acknowledge - client side wipes the UI
    return {"status": "success", "message": "Chat cleared locally."}

@app.route('/health')
def health(): return "OK"

@app.route('/admin')
def admin():
    if 'user_id' not in session: # Optionally check for 'admin' role if added later
        # return redirect(url_for('login'))
        pass # Allow access for now for demonstration

    patients = Patient.query.all()

    total = len(patients)
    high = 0
    moderate = 0
    low = 0
    recent_alerts = []

    patient_data = [] # Detailed list for admin display

    for p in patients:
        last = HealthRecord.query.filter_by(patient_id=p.id).order_by(HealthRecord.date.desc()).first()
        risk = "Unknown"
        if last:
            risk = last.risk_score or "Low"
            if "high" in risk.lower():
                high += 1
                recent_alerts.append({"message": f"Critical: High risk for patient {p.name}", "type": "error"})
            elif "moderate" in risk.lower():
                moderate += 1
            else:
                low += 1
        
        patient_data.append({
            "name": p.name,
            "email": p.email,
            "ckd_stage": p.ckd_stage,
            "latest_risk": risk,
            "id": p.id
        })

    return render_template('admin.html',
                           total_patients=total,
                           high_risk=high,
                           moderate=moderate,
                           low=low,
                           patients=patient_data,
                           alerts=recent_alerts)

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
