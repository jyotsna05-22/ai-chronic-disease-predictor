import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

DATASET_FILE = "datasets/chronoprecure_health_dataset.csv"
MODEL_DIR = "models"
MODEL_FILE = os.path.join(MODEL_DIR, "chronoprecure_model.pkl")
ENCODERS_FILE = os.path.join(MODEL_DIR, "chronoprecure_encoders.pkl")


def standardize_columns(df):
    df.columns = [str(col).strip().lower() for col in df.columns]

    rename_map = {
        "height_cm": "height_cm",
        "weight_kg": "weight_kg",
        "blood_pressure": "blood_pressure",
        "blood_pre": "blood_pressure",
        "bp": "blood_pressure",
        "cholesterol": "cholesterol",
        "cholestrol": "cholesterol",
        "cholesterc": "cholesterol",
        "sleep_hours": "sleep_hours",
        "sleep_hour": "sleep_hours",
        "sleep_hou": "sleep_hours",
        "chest_pain": "chest_pain",
        "chest_pai": "chest_pain",
        "breathing_difficulty": "breathing_difficulty",
        "breathing": "breathing_difficulty",
        "joint_pain": "joint_pain",
        "fatigue": "fatigue",
        "mood_stress": "mood_stress",
        "mood_str": "mood_stress",
        "pregnant": "pregnant",
        "pregnancy_month": "pregnancy_month",
        "pregnancy": "pregnancy_month",
        "target_disease": "target_disease",
        "disease": "target_disease"
    }

    df = df.rename(columns=rename_map)
    return df


def main():
    print("Starting ChronoPreCure model training...")

    if not os.path.exists(DATASET_FILE):
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_FILE}"
        )

    os.makedirs(MODEL_DIR, exist_ok=True)

    df = pd.read_csv(DATASET_FILE)
    df = standardize_columns(df)

    required_columns = [
        "age",
        "gender",
        "height_cm",
        "weight_kg",
        "bmi",
        "blood_pressure",
        "glucose",
        "cholesterol",
        "smoking",
        "alcohol",
        "exercise",
        "sleep_hours",
        "chest_pain",
        "breathing_difficulty",
        "joint_pain",
        "fatigue",
        "mood_stress",
        "pregnant",
        "pregnancy_month",
        "target_disease"
    ]

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in CSV: {missing}")

    df = df[required_columns].copy()

    # Clean text values
    text_columns = [
        "gender", "smoking", "alcohol", "exercise", "chest_pain",
        "breathing_difficulty", "joint_pain", "fatigue",
        "mood_stress", "pregnant", "target_disease"
    ]
    for col in text_columns:
        df[col] = df[col].astype(str).str.strip().str.lower()

    # Numeric conversion
    numeric_columns = [
        "age", "height_cm", "weight_kg", "bmi", "blood_pressure",
        "glucose", "cholesterol", "sleep_hours", "pregnancy_month"
    ]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Fill missing numeric values
    for col in numeric_columns:
        if df[col].isna().any():
            df[col] = df[col].fillna(df[col].median())

    # Fill missing text values
    for col in text_columns:
        df[col] = df[col].replace(["nan", "none", ""], "no")

    feature_columns = [
        "age",
        "gender",
        "height_cm",
        "weight_kg",
        "bmi",
        "blood_pressure",
        "glucose",
        "cholesterol",
        "smoking",
        "alcohol",
        "exercise",
        "sleep_hours",
        "chest_pain",
        "breathing_difficulty",
        "joint_pain",
        "fatigue",
        "mood_stress",
        "pregnant",
        "pregnancy_month"
    ]

    categorical_columns = [
        "gender",
        "smoking",
        "alcohol",
        "exercise",
        "chest_pain",
        "breathing_difficulty",
        "joint_pain",
        "fatigue",
        "mood_stress",
        "pregnant"
    ]

    encoders = {}

    for col in categorical_columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le

    target_encoder = LabelEncoder()
    df["target_disease"] = target_encoder.fit_transform(df["target_disease"])
    encoders["target_disease"] = target_encoder

    X = df[feature_columns]
    y = df["target_disease"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        random_state=42
    )
    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)

    joblib.dump(model, MODEL_FILE)
    joblib.dump(encoders, ENCODERS_FILE)

    print("Model trained successfully.")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Saved model to: {MODEL_FILE}")
    print(f"Saved encoders to: {ENCODERS_FILE}")


if __name__ == "__main__":
    main()