from flask import Flask, render_template, request, redirect, session, url_for, flash
import os
import joblib
import wikipedia
import re
from pymongo import MongoClient
import json
from flask_bcrypt import Bcrypt
from bson.objectid import ObjectId

# ---------------- CONFIG ----------------
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "my_secret_key_789")
bcrypt = Bcrypt(app)

# ---------------- LOAD MODEL ----------------
# Standardized paths - ensure these files are in the same folder as app.py or update accordingly
MODEL_PATH = "C:/Users/TOSHIBA/OneDrive/Desktop/Disease Predictor/disease_rf_model.pkl"
ENCODER_PATH = "C:/Users/TOSHIBA/OneDrive/Desktop/Disease Predictor/label_encoder.pkl"

model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)

# ---------------- CONNECT TO MONGODB ----------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client_db = MongoClient(MONGO_URI)
db = client_db["disease_prediction"]
users_col = db["users"]
predictions_col = db["predictions"]

# ---------------- SYMPTOMS LIST ----------------
# This list MUST match the exact order and names used during your model training
symptoms_list = [
    'itching', 'skin_rash', 'nodal_skin_eruptions', 'continuous_sneezing', 'shivering', 'chills', 
    'joint_pain', 'stomach_pain', 'acidity', 'ulcers_on_tongue', 'muscle_wasting', 'vomiting',
    'burning_micturition', 'spotting_ urination', 'fatigue', 'weight_gain', 'anxiety', 'cold_hands_and_feets',
    'mood_swings', 'weight_loss', 'restlessness', 'lethargy', 'patches_in_throat', 'irregular_sugar_level',
    'cough', 'high_fever', 'sunken_eyes', 'breathlessness', 'sweating', 'dehydration', 'indigestion',
    'headache', 'yellowish_skin', 'dark_urine', 'nausea', 'loss_of_appetite', 'pain_behind_the_eyes',
    'back_pain', 'constipation', 'abdominal_pain', 'diarrhoea', 'mild_fever', 'yellow_urine',
    'yellowing_of_eyes', 'acute_liver_failure', 'fluid_overload', 'swelling_of_stomach', 'swelled_lymph_nodes',
    'malaise', 'blurred_and_distorted_vision', 'phlegm', 'throat_irritation', 'redness_of_eyes', 'sinus_pressure',
    'runny_nose', 'congestion', 'chest_pain', 'weakness_in_limbs', 'fast_heart_rate', 'pain_during_bowel_movements',
    'pain_in_anal_region', 'bloody_stool', 'irritation_in_anus', 'neck_pain', 'dizziness', 'cramps', 'bruising',
    'obesity', 'swollen_legs', 'swollen_blood_vessels', 'puffy_face_and_eyes', 'enlarged_thyroid', 'brittle_nails',
    'swollen_extremeties', 'excessive_hunger', 'extra_marital_contacts', 'drying_and_tingling_lips', 'slurred_speech',
    'knee_pain', 'hip_joint_pain', 'muscle_weakness', 'stiff_neck', 'swelling_joints', 'movement_stiffness',
    'spinning_movements', 'loss_of_balance', 'unsteadiness', 'weakness_of_one_body_side', 'loss_of_smell',
    'bladder_discomfort', 'foul_smell_of urine', 'continuous_feel_of_urine', 'passage_of_gases', 'internal_itching',
    'toxic_look_(typhos)', 'depression', 'irritability', 'muscle_pain', 'altered_sensorium', 'red_spots_over_body',
    'belly_pain', 'abnormal_menstruation', 'dischromic _patches', 'watering_from_eyes', 'increased_appetite',
    'polyuria', 'family_history', 'mucoid_sputum', 'rusty_sputum', 'lack_of_concentration', 'visual_disturbances',
    'receiving_blood_transfusion', 'receiving_unsterile_injections', 'coma', 'stomach_bleeding', 'distention_of_abdomen',
    'history_of_alcohol_consumption', 'fluid_overload.1', 'blood_in_sputum', 'prominent_veins_on_calf', 'palpitations',
    'painful_walking', 'pus_filled_pimples', 'blackheads', 'scurring', 'skin_peeling', 'silver_like_dusting',
    'small_dents_in_nails', 'inflammatory_nails', 'blister', 'red_sore_around_nose', 'yellow_crust_ooze'
]

# ---------------- wikipedia data fetching FUNCTION ----------------
CACHE_FILE = "disease_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(data):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def extract_precautions(text):
    # Split text into sentences based on periods followed by a space
    sentences = re.split(r'\.\s+', text)
    precautions = []

    for s in sentences:
        s = s.strip()
        # Filter for sentences that look like actual advice (length check)
        # Avoid common Wikipedia artifacts like [1], [2] citations
        s = re.sub(r'\[\d+\]', '', s) 
        
        if len(s) > 30 and len(precautions) < 5:
            # Clean up the sentence to ensure it ends properly
            if not s.endswith('.'):
                s += '.'
            precautions.append(s)

    return precautions if precautions else ["Consult a healthcare professional for specific guidance."]

def get_disease_info(disease):
    cache = load_cache()

    if disease in cache:
        return cache[disease]["description"], cache[disease]["precautions"]

    try:
        # 1. Improve the search query by adding context
        search_query = f"{disease} (medical condition)"
        
        # 2. Get the page with the specific query
        page = wikipedia.page(search_query, auto_suggest=True)
        description = wikipedia.summary(search_query, sentences=2)

        # 3. Look for sections that contain actual precautions/advice
        target_sections = ["prevention", "management", "treatment", "prognosis", "lifestyle"]
        precautions_text = ""
        
        for section in page.sections:
            if any(target in section.lower() for target in target_sections):
                content = page.section(section)
                if content:
                    precautions_text += content + " "

        # 4. Extract 3-5 clean sentences
        precautions = extract_precautions(precautions_text)

        # Save to cache
        cache[disease] = {
            "description": description,
            "precautions": precautions
        }
        save_cache(cache)

        return description, precautions

    except Exception:
        # Fallback if Wikipedia fails
        return (
            f"Information regarding {disease} is not available.",
            ["Consult a medical professional for advice.", "Follow standard health protocols."]
        )

# ---------------- ROUTES ----------------

@app.route("/")
def home_page():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if users_col.find_one({"email": email}):
            flash("Email already exists! Please login instead.", "error") # Flash message
            return render_template("signup.html") # Reload page instead of returning string

        hashed = bcrypt.generate_password_hash(password).decode("utf-8")
        user_id = users_col.insert_one({
            "username": username,
            "email": email,
            "password": hashed
        }).inserted_id

        session["user_id"] = str(user_id)
        session["user_name"] = username
        return redirect(url_for("predict_page"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = users_col.find_one({"email": email})
        if user:
            if bcrypt.check_password_hash(user["password"], password):
                session["user_id"] = str(user["_id"])
                session["user_name"] = user["username"]
                return redirect(url_for("predict_page"))
            else:
                flash("Wrong password. Please try again.", "error") # Specific password error
        else:
            flash("No account found with this email.", "error") # Specific email error
            
        return render_template("login.html")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home_page"))

@app.route("/predict", methods=["GET", "POST"])
def predict_page():
    if "user_id" not in session:
        return redirect(url_for("login"))

    

    results = []

    if request.method == "POST":
        selected_raw = request.form.get("symptoms", "")
        selected_list = [s.strip() for s in selected_raw.split(",") if s.strip()]

        if selected_list:
            input_vector = [0] * len(symptoms_list)
            for s in selected_list:
                if s in symptoms_list:
                    input_vector[symptoms_list.index(s)] = 1

            # Predict probabilities
            probabilities = model.predict_proba([input_vector])[0]

            # Top 3 indices
            top_indices = probabilities.argsort()[-3:][::-1]

            for idx in top_indices:
                disease = label_encoder.inverse_transform([idx])[0]
                confidence = round(probabilities[idx] * 100, 2)

                description, precautions = get_disease_info(disease)

                results.append({
                    "disease": disease,
                    "confidence": confidence,
                    "description": description,
                    "precautions": precautions
                })

            # --- MONGODB INSERTION ---
           # --- MONGODB INSERTION ---
            try:
                # Create a list of just the disease names from your results
                disease_names = [res['disease'] for res in results]

                prediction_entry = {
                    "user_id": ObjectId(session["user_id"]),
                    "symptoms_selected": selected_list,  # Stores the symptoms user typed/selected
                    "top_3_diseases": disease_names,     # Stores the names of the 3 predicted diseases
                    "full_results": results,             # Stores descriptions/precautions/confidence
                    "timestamp": os.urandom(4).hex()     # Useful for tracking unique entries
                }
                
                predictions_col.insert_one(prediction_entry)
                print("Data stored successfully in MongoDB")
            except Exception as e:
                print(f"Error saving to database: {e}")


    return render_template(
        "predict.html",
        results=results,
        symptoms_list=symptoms_list,
        username=session.get("user_name")
    )


if __name__ == "__main__":
    app.run(debug=True)