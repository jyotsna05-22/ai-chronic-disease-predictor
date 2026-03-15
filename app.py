from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
import sqlite3
import os
import joblib
import pandas as pd

app = Flask(__name__)
app.secret_key = "secret123"

DB_NAME = "instance/health.db"
MODEL_FILE = "models/chronoprecure_model.pkl"
ENCODERS_FILE = "models/chronoprecure_encoders.pkl"

last_result = {}

# ---------------- DIET DATABASE ----------------
diet_database = {
    "Healthy": {
        "Monday": {"veg": "Oats + Fruits + Almond Milk", "nonveg": "Boiled Eggs + Whole Wheat Toast"},
        "Tuesday": {"veg": "Vegetable Soup + Multigrain Roti", "nonveg": "Grilled Chicken + Salad"},
        "Wednesday": {"veg": "Dal + Brown Rice + Curd", "nonveg": "Fish Curry + Brown Rice"},
        "Thursday": {"veg": "Paneer Bhurji + Roti + Salad", "nonveg": "Chicken Soup + Chapati"},
        "Friday": {"veg": "Fruit Smoothie + Dry Fruits", "nonveg": "Omelette + Whole Wheat Toast"},
        "Saturday": {"veg": "Mixed Vegetable Curry + Chapati", "nonveg": "Grilled Fish + Salad"},
        "Sunday": {"veg": "Vegetable Biryani (Low Oil) + Raita", "nonveg": "Chicken Biryani (Low Oil)"}
    },
    "Diabetes": {
        "Monday": {"veg": "Oats + Chia Seeds + Cinnamon", "nonveg": "Boiled Eggs + Cucumber Salad"},
        "Tuesday": {"veg": "Sprouts Salad + Multigrain Roti", "nonveg": "Grilled Chicken + Salad"},
        "Wednesday": {"veg": "Brown Rice + Dal + Curd", "nonveg": "Fish Curry + Brown Rice"},
        "Thursday": {"veg": "Paneer Bhurji + Roti + Salad", "nonveg": "Chicken Soup + Chapati"},
        "Friday": {"veg": "Low-Sugar Fruit Bowl + Nuts", "nonveg": "Omelette + Salad"},
        "Saturday": {"veg": "Vegetable Curry + Chapati", "nonveg": "Grilled Fish + Steamed Veg"},
        "Sunday": {"veg": "Vegetable Khichdi + Curd", "nonveg": "Chicken Curry + Salad"}
    },
    "Heart Disease": {
        "Monday": {"veg": "Oats + Apple + Flaxseeds", "nonveg": "Boiled Eggs + Oats"},
        "Tuesday": {"veg": "Vegetable Soup (Low Salt) + Roti", "nonveg": "Grilled Chicken (No Skin) + Salad"},
        "Wednesday": {"veg": "Dal + Brown Rice + Salad", "nonveg": "Baked Fish + Brown Rice"},
        "Thursday": {"veg": "Paneer (Low Fat) + Roti + Salad", "nonveg": "Chicken Soup + Salad"},
        "Friday": {"veg": "Fruit Smoothie (No Sugar) + Nuts", "nonveg": "Omelette (Less Oil) + Salad"},
        "Saturday": {"veg": "Mixed Veg + Chapati + Curd", "nonveg": "Grilled Fish + Veg"},
        "Sunday": {"veg": "Vegetable Upma + Buttermilk", "nonveg": "Chicken + Salad"}
    },
    "Liver Disease": {
        "Monday": {"veg": "Oats + Banana", "nonveg": "Boiled Eggs + Papaya"},
        "Tuesday": {"veg": "Vegetable Soup + Roti", "nonveg": "Grilled Chicken + Steamed Veg"},
        "Wednesday": {"veg": "Dal + Rice (Small Portion) + Curd", "nonveg": "Fish (Light Curry) + Rice"},
        "Thursday": {"veg": "Paneer (Small) + Chapati + Salad", "nonveg": "Chicken Soup + Chapati"},
        "Friday": {"veg": "Fruit Bowl (Papaya, Apple)", "nonveg": "Omelette (Low Oil)"},
        "Saturday": {"veg": "Vegetable Curry + Chapati", "nonveg": "Grilled Fish + Salad"},
        "Sunday": {"veg": "Vegetable Khichdi + Curd", "nonveg": "Chicken Stew + Salad"}
    },
    "Kidney Disease": {
        "Monday": {"veg": "Oats (Small Portion) + Apple", "nonveg": "Egg Whites + Salad"},
        "Tuesday": {"veg": "Vegetable Soup (Low Salt) + Roti", "nonveg": "Grilled Chicken (Small Portion)"},
        "Wednesday": {"veg": "Rice + Dal (Controlled Portion)", "nonveg": "Fish (Small Portion)"},
        "Thursday": {"veg": "Paneer (Small) + Chapati", "nonveg": "Chicken Soup (Low Salt)"},
        "Friday": {"veg": "Fruit Bowl (Apple, Grapes)", "nonveg": "Omelette (Low Salt)"},
        "Saturday": {"veg": "Vegetable Curry + Chapati", "nonveg": "Fish + Steamed Veg"},
        "Sunday": {"veg": "Vegetable Upma + Curd", "nonveg": "Chicken (Small Portion) + Salad"}
    },
    "Obesity": {
        "Monday": {"veg": "Oats + Fruits (No Sugar)", "nonveg": "Egg Whites + Green Tea"},
        "Tuesday": {"veg": "Vegetable Soup + Salad", "nonveg": "Grilled Chicken Salad"},
        "Wednesday": {"veg": "Dal + Brown Rice (Small)", "nonveg": "Fish + Salad"},
        "Thursday": {"veg": "Paneer Salad + Roti", "nonveg": "Chicken Salad + Lemon Water"},
        "Friday": {"veg": "Fruit Bowl + Nuts (Small)", "nonveg": "Omelette + Salad"},
        "Saturday": {"veg": "Mixed Veg + Chapati", "nonveg": "Grilled Fish + Veg"},
        "Sunday": {"veg": "Vegetable Soup + Sprouts", "nonveg": "Chicken Soup + Salad"}
    },
    "Asthma": {
        "Monday": {"veg": "Oats + Warm Water", "nonveg": "Boiled Eggs + Ginger Tea"},
        "Tuesday": {"veg": "Vegetable Soup + Roti", "nonveg": "Grilled Chicken + Soup"},
        "Wednesday": {"veg": "Dal + Brown Rice + Curd", "nonveg": "Fish + Rice"},
        "Thursday": {"veg": "Paneer + Chapati + Salad", "nonveg": "Chicken Soup"},
        "Friday": {"veg": "Fruit Smoothie (Room Temp)", "nonveg": "Omelette + Salad"},
        "Saturday": {"veg": "Vegetable Curry + Chapati", "nonveg": "Grilled Fish"},
        "Sunday": {"veg": "Vegetable Khichdi", "nonveg": "Chicken Stew"}
    },
    "Arthritis": {
        "Monday": {"veg": "Oats + Banana + Flaxseeds", "nonveg": "Boiled Eggs + Nuts"},
        "Tuesday": {"veg": "Vegetable Soup + Roti", "nonveg": "Grilled Chicken + Salad"},
        "Wednesday": {"veg": "Dal + Brown Rice + Curd", "nonveg": "Omega-3 Fish + Rice"},
        "Thursday": {"veg": "Paneer + Chapati + Salad", "nonveg": "Chicken Soup"},
        "Friday": {"veg": "Fruit Smoothie + Walnuts", "nonveg": "Omelette + Salad"},
        "Saturday": {"veg": "Mixed Veg + Chapati", "nonveg": "Grilled Fish"},
        "Sunday": {"veg": "Vegetable Khichdi + Curd", "nonveg": "Chicken + Salad"}
    },
    "Cancer Risk": {
        "Monday": {"veg": "Oats + Almond Milk + Berries", "nonveg": "Boiled Eggs + Fruits"},
        "Tuesday": {"veg": "Vegetable Soup + Salad", "nonveg": "Grilled Chicken + Salad"},
        "Wednesday": {"veg": "Dal + Brown Rice + Veg", "nonveg": "Fish + Veg"},
        "Thursday": {"veg": "Paneer + Roti + Veg", "nonveg": "Chicken Soup + Salad"},
        "Friday": {"veg": "Fruit Bowl + Nuts", "nonveg": "Omelette + Veg"},
        "Saturday": {"veg": "Mixed Veg + Chapati", "nonveg": "Fish + Veg"},
        "Sunday": {"veg": "Vegetable Upma + Salad", "nonveg": "Chicken + Veg"}
    },
    "Stroke Risk": {
        "Monday": {"veg": "Oats + Apple + Flaxseeds", "nonveg": "Boiled Eggs + Salad"},
        "Tuesday": {"veg": "Vegetable Soup (Low Salt)", "nonveg": "Grilled Chicken + Salad"},
        "Wednesday": {"veg": "Dal + Brown Rice + Veg", "nonveg": "Fish + Brown Rice"},
        "Thursday": {"veg": "Paneer (Low Fat) + Roti", "nonveg": "Chicken Soup + Veg"},
        "Friday": {"veg": "Fruit Smoothie (No Sugar)", "nonveg": "Omelette (Low Oil)"},
        "Saturday": {"veg": "Mixed Veg + Chapati", "nonveg": "Fish + Veg"},
        "Sunday": {"veg": "Vegetable Khichdi + Curd", "nonveg": "Chicken + Salad"}
    }
}

# ---------------- ADVICE DATABASE ----------------
advice_database = {
    "Healthy": {
        "prevention": [
            "Maintain a balanced diet daily.",
            "Drink enough water every day.",
            "Exercise at least 30 minutes daily.",
            "Go for regular health checkups.",
            "Sleep 7 to 8 hours every night.",
            "Avoid smoking and alcohol."
        ],
        "lifestyle": [
            "Start the day with light stretching.",
            "Avoid late-night heavy meals.",
            "Manage stress with breathing exercises.",
            "Prefer home-cooked food.",
            "Maintain healthy body weight.",
            "Avoid sitting continuously for long hours."
        ],
        "urgent": [
            "If you feel sudden severe chest pain, go to hospital immediately.",
            "Do not ignore fainting or severe dizziness.",
            "Persistent high fever needs medical help.",
            "Sudden blurred vision needs urgent checkup.",
            "Severe swelling or allergy needs emergency care.",
            "If symptoms worsen rapidly, meet doctor immediately."
        ],
        "exercise": ["Walking", "Yoga", "Cycling", "Stretching", "Light Strength Training"]
    },
    "Diabetes": {
        "prevention": [
            "Reduce sugar and refined carbohydrates.",
            "Eat more fiber-rich foods.",
            "Maintain healthy body weight.",
            "Check blood sugar regularly.",
            "Avoid smoking and reduce alcohol.",
            "Go for eye, kidney, and foot checkups."
        ],
        "lifestyle": [
            "Walk after meals.",
            "Eat meals on time.",
            "Sleep properly every night.",
            "Manage stress daily.",
            "Drink enough water.",
            "Use low-GI foods in diet."
        ],
        "urgent": [
            "Very high sugar with weakness needs urgent help.",
            "Confusion or fainting needs emergency care.",
            "Blurred vision and dehydration need fast medical help.",
            "Non-healing wounds need urgent attention.",
            "Chest pain should not be ignored.",
            "Severe sweating or collapse needs emergency care."
        ],
        "exercise": ["Walking", "Cycling", "Yoga", "Swimming", "Light Jogging"]
    },
    "Heart Disease": {
        "prevention": [
            "Reduce salt intake.",
            "Avoid oily and fried foods.",
            "Control cholesterol levels.",
            "Stop smoking completely.",
            "Keep BP and weight under control.",
            "Follow medicines regularly."
        ],
        "lifestyle": [
            "Walk daily.",
            "Choose heart-friendly foods.",
            "Practice meditation or breathing exercises.",
            "Sleep well.",
            "Reduce caffeine if needed.",
            "Avoid long sitting periods."
        ],
        "urgent": [
            "Chest pain spreading to arm or jaw is emergency.",
            "Severe breathlessness needs hospital care.",
            "Irregular heartbeat with dizziness needs urgent care.",
            "Leg swelling with breathlessness needs medical check.",
            "Sudden severe headache with high BP is serious.",
            "Stroke signs need emergency help."
        ],
        "exercise": ["Walking", "Light Cycling", "Gentle Yoga", "Breathing Exercises", "Stretching"]
    },
    "Liver Disease": {
        "prevention": [
            "Avoid alcohol completely.",
            "Reduce oily and high-sugar foods.",
            "Maintain healthy body weight.",
            "Drink clean water and eat hygienic food.",
            "Take vaccinations if advised.",
            "Do liver function tests when needed."
        ],
        "lifestyle": [
            "Eat small, light meals.",
            "Increase vegetables and lean proteins.",
            "Stay hydrated.",
            "Walk daily.",
            "Sleep properly.",
            "Avoid self-medication."
        ],
        "urgent": [
            "Yellow eyes or skin needs urgent medical care.",
            "Severe abdominal pain needs emergency checkup.",
            "Vomiting blood is emergency.",
            "Confusion or extreme drowsiness is serious.",
            "Dark urine with weakness needs fast checkup.",
            "High fever with jaundice needs hospital care."
        ],
        "exercise": ["Walking", "Gentle Yoga", "Light Cycling", "Stretching", "Low-Impact Cardio"]
    },
    "Kidney Disease": {
        "prevention": [
            "Control BP and diabetes strictly.",
            "Reduce salt intake.",
            "Drink proper amount of water.",
            "Avoid unnecessary painkiller use.",
            "Do regular kidney tests.",
            "Avoid smoking and alcohol."
        ],
        "lifestyle": [
            "Follow kidney-friendly diet.",
            "Avoid packaged salty snacks.",
            "Do light exercise.",
            "Sleep well.",
            "Monitor swelling and urination.",
            "Take medicines regularly."
        ],
        "urgent": [
            "Suddenly reduced urination is serious.",
            "Swelling with breathlessness needs urgent care.",
            "Vomiting with confusion needs emergency help.",
            "Very high BP with headache is dangerous.",
            "Blood in urine needs quick checkup.",
            "Burning urination with fever needs treatment."
        ],
        "exercise": ["Walking", "Gentle Yoga", "Stretching", "Breathing Exercises", "Light Cycling"]
    },
    "Obesity": {
        "prevention": [
            "Control food portions.",
            "Avoid sugary drinks.",
            "Eat more vegetables and fruits.",
            "Avoid daily junk food.",
            "Exercise regularly.",
            "Sleep properly."
        ],
        "lifestyle": [
            "Start the day with water and walking.",
            "Include protein in meals.",
            "Manage emotional eating.",
            "Replace junk food with healthy snacks.",
            "Do strength training if possible.",
            "Eat slowly."
        ],
        "urgent": [
            "Breathlessness during simple walking needs checkup.",
            "Chest pain needs urgent review.",
            "Severe tiredness should not be ignored.",
            "Loud snoring with daytime sleepiness needs checkup.",
            "Rapid joint pain worsening needs care.",
            "Very high BP or sugar needs urgent medical help."
        ],
        "exercise": ["Brisk Walking", "Cycling", "Light Strength Training", "Yoga", "Swimming"]
    },
    "Asthma": {
        "prevention": [
            "Avoid dust, smoke, and strong perfume.",
            "Use inhalers regularly if prescribed.",
            "Keep room and bedding clean.",
            "Avoid cold triggers.",
            "Be careful during seasonal infections.",
            "Go for regular follow-up."
        ],
        "lifestyle": [
            "Practice breathing exercises.",
            "Do gentle yoga.",
            "Drink warm water.",
            "Sleep with head slightly raised if needed.",
            "Avoid known triggers.",
            "Keep rescue inhaler nearby."
        ],
        "urgent": [
            "Severe breathlessness is emergency.",
            "Blue lips or nails need urgent care.",
            "If inhaler is not helping, go to hospital.",
            "Fast breathing with panic needs immediate care.",
            "Cough with fever needs medical check.",
            "Collapse during attack is emergency."
        ],
        "exercise": ["Breathing Exercises", "Walking", "Pranayama", "Light Cycling", "Stretching"]
    },
    "Arthritis": {
        "prevention": [
            "Maintain healthy body weight.",
            "Do joint-friendly exercise.",
            "Avoid repetitive strain.",
            "Eat anti-inflammatory foods.",
            "Use supportive footwear.",
            "Get early treatment for persistent joint pain."
        ],
        "lifestyle": [
            "Do morning stretching.",
            "Use warm compress for stiffness.",
            "Avoid sitting too long.",
            "Sleep properly.",
            "Reduce stress.",
            "Avoid excessive stairs if painful."
        ],
        "urgent": [
            "Red, swollen, hot joint needs urgent care.",
            "High fever with joint pain is serious.",
            "Sudden inability to move joint needs checkup.",
            "Severe pain not relieved by rest needs medical help.",
            "Numbness with pain needs evaluation.",
            "Severe pain after fall should not be ignored."
        ],
        "exercise": ["Stretching", "Yoga", "Swimming", "Walking", "Low-Impact Strengthening"]
    },
    "Cancer Risk": {
        "prevention": [
            "Avoid tobacco completely.",
            "Limit alcohol.",
            "Eat more fruits and vegetables.",
            "Maintain healthy body weight.",
            "Stay physically active.",
            "Go for screening if advised."
        ],
        "lifestyle": [
            "Eat nutrient-rich foods.",
            "Walk daily.",
            "Reduce stress.",
            "Sleep consistently.",
            "Drink enough water.",
            "Avoid repeated exposure to harmful smoke."
        ],
        "urgent": [
            "Unexplained weight loss needs checkup.",
            "Persistent lump needs urgent evaluation.",
            "Unusual bleeding needs medical attention.",
            "Long-lasting fatigue should be checked.",
            "Persistent cough or wound needs checkup.",
            "Symptoms lasting weeks should not be ignored."
        ],
        "exercise": ["Walking", "Yoga", "Stretching", "Light Cardio", "Breathing Exercises"]
    },
    "Stroke Risk": {
        "prevention": [
            "Control blood pressure strictly.",
            "Reduce salt and processed food.",
            "Control cholesterol.",
            "Avoid smoking.",
            "Control diabetes and obesity.",
            "Take medicines regularly."
        ],
        "lifestyle": [
            "Walk daily.",
            "Sleep properly.",
            "Reduce stress.",
            "Drink enough water.",
            "Avoid sitting too long.",
            "Eat balanced meals."
        ],
        "urgent": [
            "Face drooping, arm weakness, or speech trouble is emergency.",
            "Sudden vision loss needs hospital care.",
            "Severe sudden headache is dangerous.",
            "One-side numbness is emergency.",
            "Confusion or fainting needs immediate attention.",
            "Do not wait if stroke signs appear."
        ],
        "exercise": ["Brisk Walking", "Yoga", "Light Cycling", "Stretching", "Breathing Exercises"]
    }
}

# ---------------- DATABASE HELPERS ----------------
def get_connection():
    os.makedirs("instance", exist_ok=True)
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            age TEXT,
            height TEXT,
            weight TEXT,
            member_since TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease TEXT,
            risk TEXT,
            bmi REAL,
            date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("SELECT COUNT(*) AS count FROM profiles")
    row = cur.fetchone()
    if row["count"] == 0:
        cur.execute("""
            INSERT INTO profiles (id, name, email, age, height, weight, member_since)
            VALUES (1, 'User', 'user@email.com', '', '', '', '2026')
        """)

    conn.commit()
    conn.close()


def get_profile():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM profiles WHERE id = 1")
    row = cur.fetchone()
    conn.close()

    if row:
        return {
            "name": row["name"] if row["name"] else "User",
            "email": row["email"] if row["email"] else "user@email.com",
            "age": row["age"] if row["age"] else "",
            "height": row["height"] if row["height"] else "",
            "weight": row["weight"] if row["weight"] else "",
            "member_since": row["member_since"] if row["member_since"] else "2026"
        }

    return {
        "name": "User",
        "email": "user@email.com",
        "age": "",
        "height": "",
        "weight": "",
        "member_since": "2026"
    }


def save_profile(name, email, age, height, weight):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT member_since FROM profiles WHERE id = 1")
    existing = cur.fetchone()
    member_since = existing["member_since"] if existing and existing["member_since"] else "2026"

    cur.execute("""
        INSERT OR REPLACE INTO profiles (id, name, email, age, height, weight, member_since)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (1, name, email, age, height, weight, member_since))

    conn.commit()
    conn.close()


def save_assessment(disease, risk, bmi, date_text):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO assessments (disease, risk, bmi, date)
        VALUES (?, ?, ?, ?)
    """, (disease, risk, bmi, date_text))
    conn.commit()
    conn.close()


def get_recent_assessments(limit=5):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT disease, risk, bmi, date
        FROM assessments
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_total_assessments():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS count FROM assessments")
    row = cur.fetchone()
    conn.close()
    return row["count"] if row else 0


def get_latest_assessment():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT disease, risk, bmi, date
        FROM assessments
        ORDER BY id DESC
        LIMIT 1
    """)
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def build_result(disease, risk, bmi, date_text):
    advice = advice_database.get(disease, advice_database["Healthy"])
    return {
        "disease": disease,
        "risk": risk,
        "bmi": bmi,
        "date": date_text,
        "diet": diet_database.get(disease, diet_database["Healthy"]),
        "exercise": advice.get("exercise", []),
        "prevention": advice.get("prevention", []),
        "lifestyle": advice.get("lifestyle", []),
        "urgent": advice.get("urgent", []),
        "advice": advice
    }

# ---------------- MODEL HELPERS ----------------
FEATURE_COLUMNS = [
    "age", "gender", "height_cm", "weight_kg", "bmi", "blood_pressure",
    "glucose", "cholesterol", "smoking", "alcohol", "exercise",
    "sleep_hours", "chest_pain", "breathing_difficulty", "joint_pain",
    "fatigue", "mood_stress", "pregnant", "pregnancy_month"
]

CATEGORICAL_COLUMNS = [
    "gender", "smoking", "alcohol", "exercise", "chest_pain",
    "breathing_difficulty", "joint_pain", "fatigue", "mood_stress", "pregnant"
]


def load_model_and_encoders():
    if not os.path.exists(MODEL_FILE) or not os.path.exists(ENCODERS_FILE):
        raise FileNotFoundError("Trained model not found. Please run: python train_models.py")
    model = joblib.load(MODEL_FILE)
    encoders = joblib.load(ENCODERS_FILE)
    return model, encoders


def safe_encode(encoders, column_name, value):
    value = str(value).strip().lower()
    le = encoders[column_name]
    if value in le.classes_:
        return int(le.transform([value])[0])
    return int(le.transform([le.classes_[0]])[0])


def prepare_input_data(form_data, encoders):
    input_df = pd.DataFrame([form_data])
    for col in CATEGORICAL_COLUMNS:
        input_df[col] = input_df[col].apply(lambda x: safe_encode(encoders, col, x))
    input_df = input_df[FEATURE_COLUMNS]
    return input_df


def get_risk_from_probability(probability_percent):
    if probability_percent >= 65:
        return "High"
    elif probability_percent >= 40:
        return "Medium"
    return "Low"

# ---------------- CHATBOT ----------------
disease_info = {
    "Diabetes": "Diabetes is a condition where blood sugar levels become too high and need regular monitoring, diet control, and exercise.",
    "Heart Disease": "Heart disease is related to reduced heart health and may be associated with high blood pressure, cholesterol, chest pain, and unhealthy lifestyle.",
    "Liver Disease": "Liver disease affects the liver's ability to process nutrients and remove toxins. Healthy food and avoiding alcohol are important.",
    "Kidney Disease": "Kidney disease affects the body's filtration system and is often linked with blood pressure, diabetes, and poor kidney function.",
    "Obesity": "Obesity means excess body weight or body fat, which can increase the risk of diabetes, heart disease, and other health problems.",
    "Asthma": "Asthma affects breathing and airways, often causing wheezing, breathlessness, chest tightness, or cough.",
    "Arthritis": "Arthritis causes joint pain, swelling, and stiffness. Lifestyle care and gentle exercise are often helpful.",
    "Cancer Risk": "Cancer risk refers to patterns that may increase the chance of abnormal cell growth and needs medical screening when symptoms persist.",
    "Stroke Risk": "Stroke risk is related to reduced blood supply to the brain and is strongly linked to blood pressure, cholesterol, diabetes, and smoking.",
    "Healthy": "Healthy means your result currently does not indicate a major disease risk pattern, but regular healthy habits are still important."
}

disease_map = {
    "diabetes": "Diabetes",
    "heart disease": "Heart Disease",
    "heart": "Heart Disease",
    "liver disease": "Liver Disease",
    "liver": "Liver Disease",
    "kidney disease": "Kidney Disease",
    "kidney": "Kidney Disease",
    "obesity": "Obesity",
    "asthma": "Asthma",
    "arthritis": "Arthritis",
    "cancer risk": "Cancer Risk",
    "cancer": "Cancer Risk",
    "stroke risk": "Stroke Risk",
    "stroke": "Stroke Risk",
    "healthy": "Healthy"
}


@app.route("/chatbot", methods=["POST"])
def chatbot():
    try:
        user_message = request.form.get("message", "").strip().lower()

        if not user_message:
            return jsonify({"reply": "Please enter a question."})

        if any(word in user_message for word in ["hi", "hello", "hey", "hii", "helo"]):
            return jsonify({
                "reply": "Hello! I am your ChronoPreCure AI health guidance assistant. You can ask me about diseases, diet, exercise, prevention, urgent advice, latest result, dashboard, profile, blood pressure, glucose, cholesterol, BMI, and healthy habits."
            })

        if any(text in user_message for text in ["who are you", "what can you do", "help me", "how can you help"]):
            return jsonify({
                "reply": "I can help you understand disease risks, diet plans, exercise suggestions, prevention tips, urgent care guidance, latest saved assessment result, and how to use the ChronoPreCure system."
            })

        if any(text in user_message for text in ["my latest result", "my result", "latest result", "latest disease", "my assessment", "last result"]):
            latest = get_latest_assessment()
            if latest:
                return jsonify({"reply": f"Your latest saved result is {latest['disease']} with {latest['risk']} risk level on {latest['date']}."})
            return jsonify({"reply": "No saved assessment result found. Please complete a health assessment first."})

        if any(text in user_message for text in ["diet time", "food time", "meal time", "when should i eat", "when to eat", "what time should i eat"]):
            return jsonify({"reply": "A healthy routine is: breakfast between 7 AM and 9 AM, lunch between 12 PM and 2 PM, and dinner between 7 PM and 8:30 PM. Avoid late-night heavy meals."})

        if any(text in user_message for text in ["water", "how much water", "drink water"]):
            return jsonify({"reply": "Most people benefit from drinking enough water through the day. A common healthy habit is 2 to 3 liters daily unless a doctor has advised fluid restriction."})

        selected_disease = None
        for key, value in disease_map.items():
            if key in user_message:
                selected_disease = value
                break

        if selected_disease:
            advice = advice_database.get(selected_disease, advice_database["Healthy"])
            diet = diet_database.get(selected_disease, diet_database["Healthy"])

            if any(word in user_message for word in ["what is", "about", "meaning", "explain"]):
                return jsonify({"reply": disease_info.get(selected_disease, "This is a health condition that needs proper care and monitoring.")})

            if any(word in user_message for word in ["diet", "food", "eat", "meal", "meals"]):
                monday = diet.get("Monday", {})
                veg = monday.get("veg", "Balanced healthy food")
                nonveg = monday.get("nonveg", "Balanced healthy food")
                return jsonify({"reply": f"For {selected_disease}, a sample diet suggestion is: Veg - {veg}. Non-veg - {nonveg}. Open the Diet Plan page to see more recommendations."})

            if any(word in user_message for word in ["exercise", "workout", "activity", "activities", "physical activity"]):
                exercises = advice.get("exercise", [])
                return jsonify({"reply": f"Recommended exercises for {selected_disease} are: {', '.join(exercises)}."})

            if any(word in user_message for word in ["prevent", "prevention", "avoid", "reduce risk", "how to prevent"]):
                prevention = advice.get("prevention", [])
                return jsonify({"reply": "Prevention tips: " + " ".join(prevention[:3])})

            if any(word in user_message for word in ["lifestyle", "routine", "habits", "daily routine"]):
                lifestyle = advice.get("lifestyle", [])
                return jsonify({"reply": "Lifestyle guidance: " + " ".join(lifestyle[:3])})

            if any(word in user_message for word in ["urgent", "emergency", "danger", "doctor", "hospital", "serious"]):
                urgent = advice.get("urgent", [])
                return jsonify({"reply": "Urgent medical guidance: " + " ".join(urgent[:3])})

            return jsonify({"reply": f"I can help with {selected_disease}. Ask me about diet, exercise, prevention, lifestyle, urgent advice, or explanation."})

        if any(word in user_message for word in ["blood pressure", "bp"]):
            return jsonify({"reply": "Blood pressure is the force of blood flow in the arteries. High blood pressure may increase the risk of heart disease, kidney disease, and stroke."})

        if any(word in user_message for word in ["glucose", "sugar", "blood sugar"]):
            return jsonify({"reply": "Glucose is the level of sugar in the blood. High glucose is commonly associated with diabetes risk."})

        if "cholesterol" in user_message:
            return jsonify({"reply": "Cholesterol is a fatty substance in the blood. High cholesterol can increase the risk of heart disease and stroke."})

        if any(word in user_message for word in ["bmi", "body mass index"]):
            return jsonify({"reply": "BMI means Body Mass Index. It is calculated using height and weight and helps estimate whether body weight is in a healthy range."})

        if any(word in user_message for word in ["risk", "risk level", "low risk", "medium risk", "high risk"]):
            return jsonify({"reply": "ChronoPreCure shows Low, Medium, or High risk based on the model's prediction confidence and the health data pattern entered by the user."})

        if any(word in user_message for word in ["lose weight", "reduce weight", "weight loss"]):
            return jsonify({"reply": "To reduce weight, focus on portion control, regular walking or exercise, enough sleep, reducing junk food and sugary drinks, and eating more vegetables and protein."})

        if any(word in user_message for word in ["stay healthy", "healthy tips", "general health"]):
            healthy_advice = advice_database.get("Healthy", {})
            prevention = healthy_advice.get("prevention", [])
            return jsonify({"reply": "General healthy habits: " + " ".join(prevention[:3])})

        if "assessment" in user_message:
            return jsonify({"reply": "Open New Assessment, enter your health details such as age, height, weight, BP, glucose, cholesterol, symptoms, and lifestyle data, then submit the form to get the result."})

        if "dashboard" in user_message:
            return jsonify({"reply": "The dashboard shows total assessments, latest risk level, latest recorded date, and recent health assessment history."})

        if "profile" in user_message:
            return jsonify({"reply": "In the Profile page you can update your name, email, age, height, and weight. Click Save Profile to store the details."})

        if "diet plan" in user_message:
            return jsonify({"reply": "The Diet Plan page shows disease-specific weekly food guidance including vegetarian and non-vegetarian suggestions."})

        if "results" in user_message or "result page" in user_message:
            return jsonify({"reply": "The Results page displays the predicted disease, risk level, and guidance such as prevention, lifestyle advice, urgent medical advice, and diet support."})

        return jsonify({
            "reply": "I can answer questions about diabetes, heart disease, kidney disease, liver disease, obesity, asthma, arthritis, cancer risk, stroke risk, diet, exercise, prevention, urgent advice, assessment, dashboard, results, profile, blood pressure, glucose, cholesterol, BMI, and healthy habits."
        })

    except Exception as e:
        print("Chatbot Error:", str(e))
        return jsonify({"reply": "The chatbot had a backend error. Please try again."})

# Initialize
init_db()
model, encoders = load_model_and_encoders()

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        profile_data = get_profile()
        session["user"] = profile_data["name"]
        return redirect("/dashboard")
    return render_template("login.html")


@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot_password.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        return redirect("/login")
    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    total_assessments = get_total_assessments()
    latest = get_latest_assessment()
    recent_assessments = get_recent_assessments(5)

    latest_risk = "None"
    latest_date = "No assessment yet"

    if latest:
        latest_risk = latest["risk"]
        latest_date = latest["date"]

    return render_template(
        "dashboard.html",
        total_assessments=total_assessments,
        latest_risk=latest_risk,
        latest_date=latest_date,
        recent_assessments=recent_assessments
    )


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        age = request.form.get("age", "").strip()
        height = request.form.get("height", "").strip()
        weight = request.form.get("weight", "").strip()

        save_profile(name, email, age, height, weight)
        session["user"] = name if name else "User"
        flash("Your details updated successfully!")
        return redirect(url_for("profile"))

    profile_data = get_profile()
    return render_template("profile.html", profile=profile_data)


@app.route("/settings")
def settings():
    return render_template("settings.html")


@app.route("/statistics")
def statistics():
    latest = get_latest_assessment()
    if not latest:
        return redirect("/dashboard")

    data = build_result(
        latest["disease"],
        latest["risk"],
        latest["bmi"],
        latest["date"]
    )
    return render_template("statistics.html", data=data)


@app.route("/overview")
def overview():
    return render_template("overview.html")


@app.route("/assessment", methods=["GET", "POST"])
def assessment():
    global last_result

    if request.method == "POST":
        try:
            age = int(request.form.get("age", 0))
            gender = request.form.get("gender", "male")
            height = float(request.form.get("height", 0))
            weight = float(request.form.get("weight", 0))
            bp = int(request.form.get("bp", 0))
            glucose = int(request.form.get("glucose", 0))
            cholesterol = int(request.form.get("cholesterol", 0))

            smoking = request.form.get("smoking", "no")
            alcohol = request.form.get("alcohol", "no")
            exercise = request.form.get("exercise", "none")
            sleep = int(request.form.get("sleep", 7))

            chest = request.form.get("chest", "no")
            breath = request.form.get("breath", "no")
            joint = request.form.get("joint", "no")
            fatigue = request.form.get("fatigue", "no")
            mood = request.form.get("mood", "no")

            pregnant = request.form.get("pregnant", "no")
            preg_month_raw = request.form.get("preg_month", "").strip()
            preg_month = int(preg_month_raw) if preg_month_raw else 0

            bmi = round(weight / ((height / 100) ** 2), 2)

            form_input = {
                "age": age,
                "gender": gender,
                "height_cm": height,
                "weight_kg": weight,
                "bmi": bmi,
                "blood_pressure": bp,
                "glucose": glucose,
                "cholesterol": cholesterol,
                "smoking": smoking,
                "alcohol": alcohol,
                "exercise": exercise,
                "sleep_hours": sleep,
                "chest_pain": chest,
                "breathing_difficulty": breath,
                "joint_pain": joint,
                "fatigue": fatigue,
                "mood_stress": mood,
                "pregnant": pregnant,
                "pregnancy_month": preg_month
            }

            input_df = prepare_input_data(form_input, encoders)

            predicted_class = model.predict(input_df)[0]
            predicted_disease = encoders["target_disease"].inverse_transform([predicted_class])[0]

            probability_array = model.predict_proba(input_df)[0]
            all_probs = list(zip(encoders["target_disease"].classes_, probability_array))
            all_probs = sorted(all_probs, key=lambda x: x[1], reverse=True)

            print("Top prediction probabilities:")
            for disease_name, prob in all_probs[:5]:
                print(disease_name, round(prob * 100, 2), "%")

            max_probability = round(float(all_probs[0][1]) * 100, 2)
            risk = get_risk_from_probability(max_probability)
            now = datetime.now().strftime("%d %B %Y - %I:%M %p")

            predicted_disease = " ".join(word.capitalize() for word in predicted_disease.split())

            save_assessment(predicted_disease, risk, bmi, now)
            last_result = build_result(predicted_disease, risk, bmi, now)

            return redirect("/results")

        except Exception as e:
            return f"Error in assessment prediction: {str(e)}"

    return render_template("assessment.html")


@app.route("/results")
def results():
    global last_result

    if not last_result:
        latest = get_latest_assessment()
        if not latest:
            return redirect("/dashboard")
        last_result = build_result(
            latest["disease"],
            latest["risk"],
            latest["bmi"],
            latest["date"]
        )

    return render_template("results.html", data=last_result)


@app.route("/diet-plan")
def diet_plan():
    global last_result

    if not last_result:
        latest = get_latest_assessment()
        if not latest:
            return redirect("/dashboard")
        last_result = build_result(
            latest["disease"],
            latest["risk"],
            latest["bmi"],
            latest["date"]
        )

    return render_template("diet_plan.html", data=last_result)


if __name__ == "__main__":
    app.run(debug=True)