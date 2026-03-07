import pandas as pd
import os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

print("Starting model training...")

os.makedirs("models", exist_ok=True)

# =====================================
# COMMON PREPROCESSING (FIXED)
# =====================================
def clean_features(df):
    # Normalize invalid values
    df.replace(["?", "NA", "na", "N/A", "n/a", "", " "], np.nan, inplace=True)

    # Drop empty columns
    df.dropna(axis=1, how="all", inplace=True)

    # Strip strings safely
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()

    # Convert everything possible to numeric (FIX HERE)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Fill missing values
    for col in df.columns:
        if df[col].isna().any():
            df[col] = df[col].fillna(df[col].mean())

    return df


# =====================================
# TRAIN FUNCTIONS
# =====================================

def train_diabetes():
    df = pd.read_csv("datasets/diabetes.csv")
    df = clean_features(df)

    X = df.drop("Outcome", axis=1)
    y = df["Outcome"]

    model = RandomForestClassifier(random_state=42)
    model.fit(X, y)

    joblib.dump(model, "models/diabetes_model.pkl")
    print("diabetes_model trained ✅")


def train_heart():
    df = pd.read_csv("datasets/heart_disease_uci.csv")
    df = clean_features(df)

    # Convert multi-class to binary
    df["num"] = df["num"].apply(lambda x: 0 if x == 0 else 1)

    X = df.drop("num", axis=1)
    y = df["num"]

    model = RandomForestClassifier(random_state=42)
    model.fit(X, y)

    joblib.dump(model, "models/heart_model.pkl")
    print("heart_model trained ✅")


def train_liver():
    df = pd.read_csv("datasets/indian_liver_patient.csv")
    df = clean_features(df)

    df["Dataset"] = df["Dataset"].apply(lambda x: 1 if x == 1 else 0)

    X = df.drop("Dataset", axis=1)
    y = df["Dataset"]

    model = RandomForestClassifier(random_state=42)
    model.fit(X, y)

    joblib.dump(model, "models/liver_model.pkl")
    print("liver_model trained ✅")


def train_kidney():
    df = pd.read_csv("datasets/kidney_disease.csv")

    # Strip whitespace safely (NO applymap)
    obj_cols = df.select_dtypes(include="object").columns
    for col in obj_cols:
        df[col] = df[col].astype(str).str.strip()

    # Map target column
    df["classification"] = df["classification"].replace({
        "ckd": 1,
        "ckdt": 1,
        "notckd": 0
    })

    # Explicit medical categorical mappings
    binary_map = {
        "yes": 1, "no": 0,
        "present": 1, "notpresent": 0,
        "good": 1, "poor": 0,
        "abnormal": 1, "normal": 0
    }

    for col in obj_cols:
        if col != "classification":
            df[col] = df[col].replace(binary_map)

    # Replace invalid symbols
    df.replace(["?", "NA", "na", "N/A", "n/a", "", " "], pd.NA, inplace=True)

    # Convert all to numeric
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Fill missing values
    df.fillna(df.mean(), inplace=True)

    # Split
    X = df.drop("classification", axis=1)
    y = df["classification"]

    model = RandomForestClassifier(random_state=42)
    model.fit(X, y)

    joblib.dump(model, "models/kidney_model.pkl")
    print("kidney_model trained ✅")

def train_anemia():
    df = pd.read_csv("datasets/anemia.csv")
    df["Result"] = df["Result"].replace({"Yes": 1, "No": 0})

    df = clean_features(df)

    X = df.drop("Result", axis=1)
    y = df["Result"]

    model = RandomForestClassifier(random_state=42)
    model.fit(X, y)

    joblib.dump(model, "models/anemia_model.pkl")
    print("anemia_model trained ✅")


# =====================================
# RUN ALL
# =====================================

train_diabetes()
train_heart()
train_liver()
train_kidney()
train_anemia()

print("\n🎉 ALL MODELS TRAINED SUCCESSFULLY")