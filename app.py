from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

DB_NAME = "chronoprecure.db"
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
            "Maintain a balanced plate daily with vegetables, protein, fruits, and whole grains for long-term wellness.",
            "Drink enough water every day and reduce sugary beverages to protect metabolism and kidney health.",
            "Do at least 30 minutes of physical activity such as walking, yoga, or cycling to keep the body active.",
            "Get regular health checkups for blood pressure, sugar, and cholesterol to detect issues early.",
            "Sleep 7–8 hours consistently because good sleep supports immunity, hormones, and body recovery.",
            "Avoid smoking and limit alcohol because both increase future chronic disease risk."
        ],
        "lifestyle": [
            "Start your day with light movement such as stretching or a short walk to improve circulation.",
            "Follow regular meal timings and avoid late-night heavy eating for better digestion and energy control.",
            "Practice stress management like meditation or deep breathing to protect mental and physical health.",
            "Choose home-cooked food more often and reduce packed, fried, and processed snacks.",
            "Maintain a healthy body weight through portion control and balanced food choices.",
            "Take short breaks during long sitting periods to reduce stiffness and improve blood flow."
        ],
        "urgent": [
            "Seek urgent medical help if you experience sudden chest pain, severe breathlessness, or fainting.",
            "Go to the hospital immediately if weakness, confusion, or severe dizziness occurs suddenly.",
            "Persistent high fever, dehydration, or repeated vomiting should not be ignored.",
            "Any sudden severe headache or blurred vision needs prompt medical evaluation.",
            "Swelling of face, lips, or severe allergy signs need emergency care.",
            "If symptoms worsen rapidly, do not wait—consult a doctor immediately."
        ],
        "exercise": ["Brisk Walking", "Yoga", "Cycling", "Light Strength Training", "Stretching"]
    },

    "Diabetes": {
        "prevention": [
            "Reduce sweets, sugary drinks, and refined carbohydrates, and choose whole grains instead.",
            "Eat high-fiber foods like vegetables, oats, dals, and sprouts to slow glucose spikes.",
            "Maintain a healthy body weight because weight control improves insulin sensitivity.",
            "Check blood sugar regularly and follow medication or insulin plans consistently.",
            "Avoid smoking and reduce alcohol intake as both worsen blood vessel and nerve damage.",
            "Have regular eye, kidney, and foot checkups to catch complications early."
        ],
        "lifestyle": [
            "Walk for 20–40 minutes after meals, especially after dinner, to improve glucose control.",
            "Eat small, balanced meals at regular times and do not skip breakfast.",
            "Sleep 7–8 hours because poor sleep increases insulin resistance and appetite.",
            "Manage stress with yoga, meditation, or breathing exercises because stress raises sugar levels.",
            "Drink enough water daily and avoid packaged juices or soft drinks.",
            "Use low-GI foods like millets, oats, and brown rice while controlling portions."
        ],
        "urgent": [
            "Get urgent medical help if sugar levels stay very high with weakness, nausea, or vomiting.",
            "Seek emergency care if you develop confusion, fainting, seizures, or very low sugar symptoms.",
            "Blurred vision, severe dizziness, or dehydration signs need fast medical evaluation.",
            "Any non-healing wound, foot infection, or black discoloration requires urgent attention.",
            "Chest pain or sudden breathlessness in diabetes should never be ignored.",
            "Repeated severe sweating, shaking, or collapse needs immediate hospital care."
        ],
        "exercise": ["Brisk Walking", "Cycling", "Yoga", "Swimming", "Light Jogging"]
    },

    "Heart Disease": {
        "prevention": [
            "Reduce salt intake by limiting pickles, chips, instant food, and processed snacks.",
            "Avoid saturated and trans fats from fried foods, bakery items, and fast food.",
            "Maintain healthy cholesterol through fiber-rich foods like oats, fruits, and vegetables.",
            "Stop smoking completely because tobacco damages blood vessels and increases heart attack risk.",
            "Keep blood pressure and weight under control with regular monitoring and treatment.",
            "Follow all prescribed medications consistently and do routine cardiac checkups."
        ],
        "lifestyle": [
            "Walk daily for 30–45 minutes at a moderate pace unless your doctor advises restrictions.",
            "Choose heart-friendly foods like fruits, salads, dal, nuts, and fish instead of fried meals.",
            "Practice breathing exercises or meditation daily to reduce stress-related BP spikes.",
            "Sleep 7–8 hours and avoid very heavy meals late at night.",
            "Reduce caffeine and energy drinks if palpitations or anxiety increase.",
            "Avoid long sitting and take movement breaks to support circulation."
        ],
        "urgent": [
            "Call emergency services if chest pressure or pain spreads to the arm, jaw, or back.",
            "Severe breathlessness, fainting, or extreme sweating needs immediate hospital care.",
            "Fast irregular heartbeat with dizziness should be checked urgently.",
            "Swelling in the legs with shortness of breath may signal heart failure and needs care.",
            "Sudden severe headache with very high BP must be treated urgently.",
            "Any stroke signs like speech trouble or face drooping require emergency help."
        ],
        "exercise": ["Walking", "Light Cycling", "Yoga (Gentle)", "Breathing Exercises", "Stretching"]
    },

    "Liver Disease": {
        "prevention": [
            "Avoid alcohol completely because it directly damages liver cells and worsens inflammation.",
            "Limit oily, fried, and high-sugar foods to reduce fatty liver progression.",
            "Maintain a healthy weight because obesity strongly increases fatty liver risk.",
            "Drink clean water and eat hygienic food to prevent hepatitis and infections.",
            "Take hepatitis vaccination if advised by a doctor and avoid unsafe injections or shared razors.",
            "Do liver function tests regularly if you have symptoms or known risk factors."
        ],
        "lifestyle": [
            "Eat small, light meals and avoid heavy late-night dinners to reduce liver workload.",
            "Choose lean proteins and increase vegetables while reducing red meat and junk food.",
            "Stay hydrated and avoid sugary beverages or artificial juices.",
            "Walk daily for at least 30 minutes to improve metabolism and liver health.",
            "Sleep properly and reduce stress because metabolic stress affects the liver.",
            "Avoid self-medication and unnecessary supplements without doctor advice."
        ],
        "urgent": [
            "Yellow eyes or skin (jaundice) that appears or worsens needs urgent medical care.",
            "Severe abdominal pain, vomiting blood, or black stools require emergency attention.",
            "Confusion, extreme sleepiness, or behavior changes can be serious liver warning signs.",
            "Swollen abdomen with breathlessness needs urgent evaluation.",
            "Persistent vomiting, dark urine, or pale stools should be checked quickly.",
            "High fever with jaundice or severe weakness requires hospital assessment."
        ],
        "exercise": ["Walking", "Yoga (Gentle)", "Light Cycling", "Stretching", "Low-Impact Cardio"]
    },

    "Kidney Disease": {
        "prevention": [
            "Control blood pressure and diabetes strictly because both are major kidney damage causes.",
            "Reduce salt and avoid processed foods to prevent fluid retention and BP strain.",
            "Drink the right amount of water as advised by your doctor based on kidney status.",
            "Avoid frequent painkiller use without medical advice because it harms kidney function.",
            "Do regular kidney tests like creatinine and urine protein if you are at risk.",
            "Avoid smoking and alcohol because they worsen blood vessel damage and kidney decline."
        ],
        "lifestyle": [
            "Follow a kidney-friendly diet with controlled salt and balanced protein intake.",
            "Avoid packaged snacks and highly processed foods that increase sodium load.",
            "Do light exercise like walking or yoga to improve circulation and blood pressure.",
            "Sleep 7–8 hours and maintain a steady daily routine to support recovery.",
            "Track swelling and changes in urination pattern regularly.",
            "Take prescribed medicines exactly as advised and never self-medicate."
        ],
        "urgent": [
            "Go to the hospital if urination becomes very low or stops suddenly.",
            "Severe swelling in legs or face with breathlessness needs urgent care.",
            "Persistent vomiting, confusion, or extreme weakness requires immediate evaluation.",
            "Very high blood pressure with headache or blurred vision is an emergency.",
            "Blood in urine or severe back pain should be checked urgently.",
            "Fever with burning urination may indicate infection and needs quick treatment."
        ],
        "exercise": ["Walking", "Yoga (Gentle)", "Stretching", "Breathing Exercises", "Light Cycling"]
    },

    "Obesity": {
        "prevention": [
            "Control portion sizes and avoid sugary drinks because liquid calories cause rapid weight gain.",
            "Eat more high-fiber foods like vegetables, fruits, salads, and dals to stay full longer.",
            "Limit daily fried foods, bakery items, and packaged snacks that increase fat storage.",
            "Track your weight and waist size regularly to notice unhealthy changes early.",
            "Do at least 150 minutes of exercise per week to prevent progressive weight gain.",
            "Sleep 7–8 hours because poor sleep increases cravings and hunger hormones."
        ],
        "lifestyle": [
            "Begin the day with water and a short walk to improve metabolism and appetite control.",
            "Include protein in every meal to reduce cravings and overeating.",
            "Avoid emotional eating by managing stress through yoga, journaling, or meditation.",
            "Replace junk snacks with fruits, sprouts, nuts in small portions, or buttermilk.",
            "Do strength training 2–3 times weekly to improve metabolism and body composition.",
            "Avoid screen-time eating and eat slowly to recognize fullness better."
        ],
        "urgent": [
            "See a doctor if breathlessness happens during normal walking or climbing stairs.",
            "Chest pain, fainting, or extreme fatigue in obesity needs urgent medical review.",
            "Loud snoring with daytime sleepiness may indicate sleep apnea and requires evaluation.",
            "Rapidly worsening joint pain or swelling should be medically assessed.",
            "Very high BP or high sugar symptoms must be checked immediately.",
            "Any depression, binge eating, or severe body image distress needs professional help."
        ],
        "exercise": ["Brisk Walking", "Cycling", "Strength Training (Light)", "Yoga", "Swimming"]
    },

    "Asthma": {
        "prevention": [
            "Avoid triggers like dust, smoke, strong perfumes, cold air, and polluted environments.",
            "Use inhalers and controller medicines exactly as prescribed and do not skip them.",
            "Keep your room and bedding clean to reduce dust mites and allergen exposure.",
            "Take preventive measures during seasonal infections because colds often trigger attacks.",
            "Warm up before exercise and avoid heavy activity in cold air without precautions.",
            "Get regular follow-up with your doctor to review symptoms and inhaler technique."
        ],
        "lifestyle": [
            "Practice breathing exercises daily to improve lung control and reduce panic during symptoms.",
            "Do gentle yoga and stretching because it helps breathing and lowers stress.",
            "Drink warm water or warm herbal fluids if cold drinks trigger symptoms.",
            "Sleep with your head slightly elevated if night cough or wheezing increases.",
            "Maintain a healthy diet and avoid known food triggers if any worsen symptoms.",
            "Always keep your rescue inhaler accessible and learn your early warning signs."
        ],
        "urgent": [
            "Emergency if severe breathlessness or chest tightness makes it hard to speak.",
            "Blue lips, nails, or severe wheezing needs immediate hospital care.",
            "If your rescue inhaler is not helping after repeated use, go to emergency.",
            "Rapid breathing with panic or sweating requires urgent medical attention.",
            "Severe cough with fever may signal infection and needs medical evaluation.",
            "Any fainting, collapse, or extreme fatigue during an attack is an emergency."
        ],
        "exercise": ["Breathing Exercises", "Walking (Moderate)", "Yoga (Pranayama)", "Light Cycling", "Stretching"]
    },

    "Arthritis": {
        "prevention": [
            "Maintain a healthy body weight because extra weight increases pressure on the joints.",
            "Do joint-friendly exercises regularly to preserve mobility and reduce stiffness.",
            "Avoid repetitive strain and use correct posture while sitting, standing, and working.",
            "Eat anti-inflammatory foods such as fish, nuts, seeds, turmeric, and vegetables.",
            "Use supportive footwear and avoid standing for too long without breaks.",
            "Get early medical advice when swelling or pain persists to slow joint damage."
        ],
        "lifestyle": [
            "Start the day with gentle stretching and warm-up to reduce morning stiffness.",
            "Use warm compresses or warm baths for stiffness relief and easier joint movement.",
            "Take breaks during long sitting periods to avoid joint locking and pain.",
            "Sleep properly and reduce stress because stress worsens pain sensitivity.",
            "Avoid excessive stairs, squatting, or lifting if knee or back joints are affected.",
            "Strengthen surrounding muscles with guided low-impact exercises."
        ],
        "urgent": [
            "Seek urgent care if a joint becomes very swollen, red, hot, and painful suddenly.",
            "High fever with joint pain may suggest infection and needs fast treatment.",
            "Sudden inability to move a joint or severe deformity requires immediate care.",
            "Pain that is not relieved with medicine or rest should be checked urgently.",
            "Numbness or tingling with back or neck pain needs medical evaluation.",
            "Any severe pain after a fall or injury should not be ignored."
        ],
        "exercise": ["Stretching", "Yoga", "Swimming", "Walking", "Low-Impact Strengthening"]
    },

    "Cancer Risk": {
        "prevention": [
            "Avoid tobacco in all forms because it is one of the strongest cancer risk factors.",
            "Limit alcohol and reduce processed meats, fried foods, and heavily packaged foods.",
            "Eat more antioxidant-rich foods like vegetables, fruits, nuts, and seeds daily.",
            "Maintain healthy weight and stay active because obesity increases several cancer risks.",
            "Protect yourself from excessive sun exposure and use sunscreen when needed.",
            "Do screening tests regularly if you have family history or persistent symptoms."
        ],
        "lifestyle": [
            "Follow a nutrient-rich diet with protein, vegetables, and fruits to support healthy cells.",
            "Stay physically active through walking, yoga, or gentle exercise every day.",
            "Reduce chronic stress and improve emotional health because immunity is affected by stress.",
            "Sleep consistently and avoid long periods of exhaustion or irregular lifestyle.",
            "Drink enough water and avoid frequent outside junk food or smoked foods.",
            "Reduce repeated exposure to harmful smoke, chemicals, and polluted environments."
        ],
        "urgent": [
            "See a doctor if unexplained weight loss occurs without dieting or exercise change.",
            "Persistent lump or swelling anywhere in the body should be checked quickly.",
            "Unusual bleeding, chronic cough, or non-healing wounds require evaluation.",
            "Continuous fatigue, appetite loss, or long-lasting pain needs medical consultation.",
            "Sudden major change in bowel habits or swallowing difficulty needs urgent review.",
            "Any symptom that persists for weeks should be evaluated instead of delayed."
        ],
        "exercise": ["Walking", "Yoga", "Stretching", "Light Cardio", "Breathing Exercises"]
    },

    "Stroke Risk": {
        "prevention": [
            "Control blood pressure strictly because high BP is the biggest stroke risk factor.",
            "Reduce salt and avoid processed snacks, pickles, and packaged foods daily.",
            "Maintain healthy cholesterol by reducing fried food and increasing fiber intake.",
            "Avoid smoking completely and limit alcohol because both damage blood vessels.",
            "Manage diabetes and obesity properly to reduce clot and artery damage risk.",
            "Do regular BP, sugar, and cholesterol checks and follow medicines consistently."
        ],
        "lifestyle": [
            "Walk daily for 30–45 minutes to improve circulation and control blood pressure.",
            "Sleep 7–8 hours and avoid heavy late-night eating to reduce metabolic strain.",
            "Reduce stress using meditation or breathing exercises because stress spikes BP.",
            "Drink enough water and avoid dehydration which can worsen clot risk.",
            "Avoid sitting too long and stretch every hour to support blood flow.",
            "Follow regular meals and reduce junk food to protect heart and brain vessels."
        ],
        "urgent": [
            "Emergency if face drooping, arm weakness, or speech difficulty occurs suddenly.",
            "Sudden vision loss, severe dizziness, or balance loss needs immediate hospital care.",
            "A severe sudden headache can be dangerous and needs urgent evaluation.",
            "Numbness on one side of the body should be treated as an emergency.",
            "Confusion, fainting, or sudden severe weakness requires immediate medical attention.",
            "Do not wait for symptoms to improve—stroke treatment works best when started early."
        ],
        "exercise": ["Brisk Walking", "Yoga", "Light Cycling", "Stretching", "Breathing Exercises"]
    }
}

# ---------------- DATABASE HELPERS ----------------
def get_connection():
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
            "name": row["name"] or "User",
            "email": row["email"] or "user@email.com",
            "age": row["age"] or "",
            "height": row["height"] or "",
            "weight": row["weight"] or "",
            "member_since": row["member_since"] or "2026"
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
    cur.execute("""
        UPDATE profiles
        SET name = ?, email = ?, age = ?, height = ?, weight = ?
        WHERE id = 1
    """, (name, email, age, height, weight))
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

# initialize database once
init_db()

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["user"] = "demo"
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
        age = int(request.form["age"])
        height = float(request.form["height"])
        weight = float(request.form["weight"])
        bp = int(request.form["bp"])
        glucose = int(request.form["glucose"])
        cholesterol = int(request.form["cholesterol"])

        chest = request.form.get("chest", "no")
        breath = request.form.get("breath", "no")
        joint = request.form.get("joint", "no")
        fatigue = request.form.get("fatigue", "no")
        smoking = request.form.get("smoking", "no")
        alcohol = request.form.get("alcohol", "no")

        bmi = round(weight / ((height / 100) ** 2), 2)

        disease = "Healthy"
        risk = "Low"

        if glucose > 140:
            disease = "Diabetes"
            risk = "High"
        elif chest == "yes" or cholesterol > 240:
            disease = "Heart Disease"
            risk = "High"
        elif bp > 160:
            disease = "Stroke Risk"
            risk = "High"
        elif alcohol == "regular" and fatigue == "yes":
            disease = "Liver Disease"
            risk = "Medium"
        elif bp > 145 and fatigue == "yes" and age > 50:
            disease = "Kidney Disease"
            risk = "Medium"
        elif bmi >= 30:
            disease = "Obesity"
            risk = "Medium"
        elif breath == "yes":
            disease = "Asthma"
            risk = "Medium"
        elif joint == "yes" and age > 45:
            disease = "Arthritis"
            risk = "Medium"
        elif smoking == "yes" and age > 55 and fatigue == "yes":
            disease = "Cancer Risk"
            risk = "Medium"

        now = datetime.now().strftime("%d %B %Y - %I:%M %p")

        save_assessment(disease, risk, bmi, now)
        last_result = build_result(disease, risk, bmi, now)

        return redirect("/results")

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