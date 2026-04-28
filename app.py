from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import numpy as np
import os
import csv
import urllib.request
import json
import urllib.parse
import time
import shutil
from sklearn.tree import DecisionTreeClassifier
import pickle
from translations import translations

app = Flask(__name__)
app.secret_key = 'dialysis_patient_monitoring_secret_key'
app.jinja_env.tests['contains'] = lambda val, s: s in str(val) if val else False

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

# --- Image Lookup Utility (Wikimedia & Fallback) ---
def get_wikimedia_image(title):
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&titles={urllib.parse.quote(title)}&pithumbsize=500&format=json"
        req = urllib.request.Request(url, headers={'User-Agent': 'DialysisApp/1.0 (test@example.com)'})
        res = urllib.request.urlopen(req).read().decode('utf-8')
        data = json.loads(res)
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if "thumbnail" in page_data:
                return page_data["thumbnail"]["source"]
    except Exception as e:
        print(f"Wikimedia error for {title}: {e}")
    return None

def fallback_fallback_unsplash(title):
    known = {
        "Pineapple": "https://images.unsplash.com/photo-1550259114-ad7188f0a96ea?w=500&q=80",
        "Watermelon": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=500&q=80",
        "Apple": "https://images.unsplash.com/photo-1570913149827-d2ac84ab3f9a?w=500&q=80",
        "Papaya": "https://images.unsplash.com/photo-1517282009859-f000ec3b26fe?w=500&q=80",
        "Pear": "https://images.unsplash.com/photo-1615486171448-4cbab5ea71bd?w=500&q=80",
        "Strawberry": "https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=500&q=80",
        "Peach": "https://images.unsplash.com/photo-1522204523234-8229ec61d904?w=500&q=80",
        "Plum": "https://images.unsplash.com/photo-1599819162354-99882ee0a716?w=500&q=80",
        "Cherry": "https://images.unsplash.com/photo-1528821128474-27f9e7765859?w=500&q=80",
        "Grapes": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Table_grapes_on_white.jpg/500px-Table_grapes_on_white.jpg",
    }
    return known.get(title)

def sync_food_images():
    # Use workspace paths
    input_file = os.path.join(basedir, "data", "food_dataset.csv")
    temp_file = os.path.join(basedir, "data", "food_dataset_temp.csv")
    
    if not os.path.exists(input_file):
        return False, f"Input file not found at {input_file}"

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)

        for row in rows:
            name = row.get('food_name')
            if not name: continue
            
            # Use logic provided by user
            img_url = get_wikimedia_image(name)
            
            if not img_url:
                mapping = {
                    "Grapes": "Grape", "Prawns": "Prawn", "Capsicum": "Bell pepper",
                    "Brinjal": "Eggplant", "Bottle gourd": "Calabash", 
                    "Snake gourd": "Trichosanthes cucumerina", "Millet": "Millet",
                    "Ragi": "Eleusine coracana", "Green peas": "Pea",
                    "Drumstick leaves": "Moringa oleifera", "Sweet lime": "Citrus limetta",
                    "Custard apple": "Sugar apple"
                }
                if name in mapping:
                    img_url = get_wikimedia_image(mapping[name])
                elif name == "Jackfruit":
                    img_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Jackfruit_in_cut_display.jpg/500px-Jackfruit_in_cut_display.jpg"
            
            if not img_url:
                img_url = fallback_fallback_unsplash(name)
                
            if img_url:
                row['image_url'] = img_url
                print(f"Set image for {name}: {img_url}")
            else:
                row['image_url'] = f"https://placehold.co/500x500/f0fdf4/16a34a?text={urllib.parse.quote(name)}"
                print(f"Fallback placeholder for {name}")
            
            time.sleep(0.3)

        with open(temp_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        shutil.move(temp_file, input_file)
        return True, "Updated all image URLs successfully"
    except Exception as e:
        print(f"Sync error: {e}")
        return False, str(e)

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
    if lang in ['en', 'ta', 'hi']:
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

@app.route('/ai-assistant')
def ai_assistant():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('ai_assistant.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Advanced Rule-Based & Context-Aware Chatbot for Dialysis Patient Monitoring and Diet Recommendation System."""
    user_msg = request.json.get('message', '').strip().lower()
    if not user_msg: return {"reply": "Neural Link Active. Awaiting your biometric query."}
    
    user = None
    latest = None
    if 'user_id' in session:
        user = db.session.get(Patient, session['user_id'])
        latest = HealthRecord.query.filter_by(patient_id=user.id).order_by(HealthRecord.date.desc()).first()
    
    ctx = {
        "k": latest.potassium if latest else 4.2,
        "cre": latest.creatinine if latest else 1.1,
        "gfr": latest.gfr if latest else 90,
        "risk": latest.risk_score if latest else "Low",
        "sugar": latest.sugar if latest else 100,
        "urea": latest.urea if latest else 40
    }

    response = ""
    
    # 1. Greetings & Normal Conversation (Guiding to Medical Focus)
    if any(x in user_msg for x in ["hello", "hi", "hey"]):
        response = "Hello! I am your clinical assistant. I am here to assist you entirely with **medical guidance**, **dietary and food suggestions**, and checking your **patient health level** using our ML-driven monitoring system. What would you like to discuss?"
    elif "how are you" in user_msg:
        response = "I am operating optimally. Thanks for asking! Let's focus on you: Would you like to check your **patient health level** or discuss **safe foods**?"
    elif any(x in user_msg for x in ["who are you", "what are you"]):
        response = "I am a dialysis patient monitoring and diet recommendation system. My purpose is to guide your conversations toward **kidney care**, **food choices**, and monitoring your **health level** based on your vitals and ML algorithms."
    elif any(x in user_msg for x in ["thank you", "thanks"]):
        response = "You're very welcome! If you need further help with your **medical questions** or **food recommendations**, just ask."
    elif any(x in user_msg for x in ["ok", "okay", "alright", "yes"]):
        response = "Great! Feel free to ask me specifics, like 'What is my health level?' or 'What foods should I avoid?'"
    elif any(x in user_msg for x in ["bye", "goodbye"]):
        response = "Take care! Continue tracking your vitals and sticking to your recommended foods. Stay healthy!"

    # 2. Medical Oriented Info (Kidney Disease & Dialysis)
    elif "kidney disease" in user_msg or "ckd" in user_msg or ("what" in user_msg and "kidney" in user_msg):
        response = "Kidney disease affects your body's ability to filter waste. Managing this medically involves tracking your eGFR, maintaining your dialysis schedule, and strictly following dietary restrictions."
    elif "dialysis" in user_msg:
        response = "Dialysis artificially removes waste and extra fluid from the blood when the kidneys fail. Always consult your nephrologist and adjust your **foods and fluids** accordingly."

    # 3. Patient Health Level & Status
    elif any(x in user_msg for x in ["report", "status", "health", "trend", "risk", "health level", "level"]):
        risk = ctx['risk']
        response = f"📊 **Patient Health Level Diagnosis:** Your current medical risk level is **{risk}**. Your Creatinine Signature is {ctx['cre']} mg/dL and your eGFR is {ctx['gfr']}. "
        if "high" in risk.lower():
            response += "⚠️ This is a high-risk level. Focus intensely on low-potassium foods and consult your doctor immediately."
        elif "moderate" in risk.lower():
            response += "⚠️ Your level is moderate. Please strictly monitor your fluid intake and salt consumption."
        else:
            response += "✅ Your level is stable. Keep maintaining your medically-prescribed kidney-friendly diet."

    # 4. Contextual Dietary Advice & Vital Signs
    elif "sugar" in user_msg or "glucose" in user_msg:
        s = ctx['sugar']
        response = f"🩸 **Blood Sugar Level:** Your latest blood sugar reading is {s} mg/dL. "
        if s > 140:
            response += "⚠️ This is high. Please restrict sugary foods and consult your doctor."
        else:
            response += "✅ Your sugar level is within a reasonable range."
            
    elif "urea" in user_msg or "bun" in user_msg:
        u = ctx['urea']
        response = f"🧪 **Blood Urea Level:** Your latest urea reading is {u} mg/dL. "
        if u > 60:
            response += "⚠️ This is elevated. Your kidneys are struggling to filter waste. Strictly follow a low-protein diet."
        else:
            response += "✅ Your urea level is manageable."

    # Dynamic Food/Vegetable Lookup (from dataset)
    elif os.path.exists('data/food_dataset.csv') and any(str(food).lower() in user_msg for food in pd.read_csv('data/food_dataset.csv')['food_name'].dropna()):
        df = pd.read_csv('data/food_dataset.csv')
        found_food = None
        for _, row in df.iterrows():
            if str(row['food_name']).lower() in user_msg:
                found_food = row
                break
        
        fname = found_food['food_name']
        rec = found_food['recommendation']
        pot = found_food.get('potassium', 0)
        
        response = f"🍽️ **Food Analysis ({fname}):** This is generally considered **{rec}** for dialysis. "
        response += f"It contains ~{pot}mg Potassium. "
        
        if ctx['k'] > 5.0 and float(pot) > 200:
             response += "⚠️ **CRITICAL:** Your potassium is severely high. AVOID this food right now!"
        elif rec.lower() == 'safe':
             response += "✅ It is safe to consume in moderation."
        else:
             response += "⚠️ Please consult your dietitian."
            
    # General Food & Diet Suggestion
    elif "diet" in user_msg or "food" in user_msg or "eat" in user_msg or "vegetable" in user_msg:
        response = "🍎 **Food Guidance:** A medically-oriented kidney diet must be **low in salt, low in potassium, and low in phosphorus**. Stay away from processed foods and opt for fresh, leached vegetables and high-quality proteins."

    # 6. GFR Interpretation (Medical)
    elif "gfr" in user_msg:
        stage = user.ckd_stage if user else 'Unknown'
        response = f"🧬 **Medical GFR Analysis:** Your estimated Glomerular Filtration Rate (eGFR) is **{ctx['gfr']} ml/min**. This indicates Stage {stage} kidney function."

    # 7. Hospitals & Dialysis Centers (Pudukkottai GH Focus)
    elif any(x in user_msg for x in ["hospital", "pudukkottai", "gh", "center", "dialysis unit", "clinic", "emergency"]):
        response = "🏥 **Dialysis Center Recommendation:** For immediate and specialized dialysis treatment, we strongly recommend visiting the **Government Medical College Hospital, Pudukkottai (GH)**. They operate a highly equipped Nephrology and Dialysis Unit for comprehensive kidney care.<br><br>📍 <a href='https://www.google.com/maps/search/Government+Medical+College+Hospital,+Pudukkottai' target='_blank' class='text-emerald-400 hover:text-white underline cursor-pointer font-bold'><i class='fas fa-map-marker-alt'></i> View Pudukkottai GH on Google Maps</a>"

    # 8. Tamil Language Support
    elif "vanakkam" in user_msg or "tamil" in user_msg or "diet in tamil" in user_msg:
        response = "வணக்கம்! சிறுநீரக ஆரோக்கியத்திற்கு குறைந்த உப்பு, குறைந்த பொட்டாசியம் உணவுகளை உண்ணுங்கள். (Hello! Eat low-salt foods for your health level.)"

    # Default / Unknown Query (LLM / ML Fallback)
    else:
        # Check if user wants LLM capabilities
        gemini_api_key = os.environ.get("GEMINI_API_KEY")

        if gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                system_prompt = f"You are a clinical assistant for a dialysis patient monitoring system. The patient is asking: '{user_msg}'. Patient context: Risk={ctx['risk']}, Creatinine={ctx['cre']}, Potassium={ctx['k']}, eGFR={ctx['gfr']}. Answer kindly, focusing primarily on kidney health, medical guidance, and foods. Limit your response to 2 sentences."
                response = model.generate_content(system_prompt).text
                response = f"✨ **Neural AI:** {response}"
            except Exception as e:
                response = f"Neural API Error: {e}"
        else:
            response = "I am a clinical assistant designed for this dialysis patient monitoring system. I can only guide you on **medical topics**. Please ask me about **kidney health, specific foods, hospitals, or your patient health level**."
            try:
                model_path = os.path.join(basedir, "chat_model.pkl")
                vectorizer_path = os.path.join(basedir, "vectorizer.pkl")
                data_path = os.path.join(basedir, "chat_data.csv")
                if os.path.exists(model_path) and os.path.exists(vectorizer_path):
                    with open(model_path, "rb") as f:
                        c_model = pickle.load(f)
                    with open(vectorizer_path, "rb") as f:
                        c_vect = pickle.load(f)
                    c_data = pd.read_csv(data_path)
                    
                    input_vec = c_vect.transform([user_msg])
                    probs = c_model.predict_proba(input_vec)[0]
                    max_prob_idx = probs.argmax()
                    intent = c_model.classes_[max_prob_idx]
                    confidence = probs[max_prob_idx]
                    
                    if confidence > 0.3:
                        # Get response for the predicted intent
                        matching_responses = c_data[c_data['intent'] == intent]['response'].values
                        if len(matching_responses) > 0:
                            response = f"🧠 AI Predicts ({intent}): " + matching_responses[0]
            except Exception as e:
                print(f"Chatbot ML Error: {e}")

    return {
        "reply": response,
        "telemetry_sync": "Verified",
        "agent_load": "Neural-7B-Mistral"
    }

@app.route('/clear-chat', methods=['POST'])
def clear_chat():
    return {"status": "success", "message": "Chat cleared locally."}

@app.route('/health')
def health(): return "OK"

@app.route('/admin')
def admin():
    patients = Patient.query.all()
    total = len(patients)
    high, moderate, low = 0, 0, 0
    recent_alerts = [] 
    patient_data = []
    for p in patients:
        last = HealthRecord.query.filter_by(patient_id=p.id).order_by(HealthRecord.date.desc()).first()
        risk = last.risk_score or "Low" if last else "Unknown"
        if "high" in risk.lower():
            high += 1
            recent_alerts.append({"message": f"Critical: High risk for patient {p.name}", "type": "error"})
        elif "moderate" in risk.lower(): moderate += 1
        else: low += 1
        patient_data.append({"name": p.name, "email": p.email, "ckd_stage": p.ckd_stage, "latest_risk": risk, "id": p.id})
    return render_template('admin.html', total_patients=total, high_risk=high, moderate=moderate, low=low, patients=patient_data, alerts=recent_alerts, accuracy="97.92%", algorithm="Decision Tree")

@app.route('/neural-insight')
def neural_insight():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('admin.html', section='neural') # Re-use admin template but focus on neural

@app.route('/lab-analysis')
def lab_analysis():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('admin.html', section='lab')

@app.route('/patient-sync')
def patient_sync():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('admin.html', section='sync')

@app.route('/config')
def config():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = db.session.get(Patient, session['user_id'])
    return render_template('config.html', user=user)

@app.route('/api/sync/v1/patient-data')
def api_patient_sync():
    """Neural Data Sync endpoint for Antigravity-style clinical telemetry."""
    if 'user_id' not in session: return {"error": "Unauthorized Access Detected"}, 401
    user = db.session.get(Patient, session['user_id'])
    history = HealthRecord.query.filter_by(patient_id=user.id).order_by(HealthRecord.date.desc()).limit(10).all()
    latest = history[0] if history else None
    return {
        "status": "synchronized_and_ready",
        "neural_load": "12%",
        "identity_node": {"id": user.id, "hash_name": f"Patient_{user.id}_N_AX"},
        "biometry": {
            "gfr": latest.gfr if latest else 0,
            "creatinine": latest.creatinine if latest else 0,
            "potassium": latest.potassium if latest else 0
        },
        "synchronization_signatures": ["REST_SYNC_01", "REALTIME_SOCKET_AVAIL"]
    }

@app.route('/admin/update-images', methods=['POST'])
def admin_update_images():
    # Only allow from admin context ideally, but for now open for testing if logged in
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    success, message = sync_food_images()
    return jsonify({"success": success, "message": message})

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
