
from pathlib import Path
import json

import joblib
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "ml" / "models" / "churn_model.joblib"
THRESHOLD_PATH = BASE_DIR / "ml" / "models" / "churn_thresholds.json"


# ============================================================
# LOAD MODEL AND THRESHOLDS
# ============================================================

model = joblib.load(MODEL_PATH)

with THRESHOLD_PATH.open("r", encoding="utf-8") as file:
    threshold_config = json.load(file)

RISK_THRESHOLDS = threshold_config["risk_thresholds"]

MEDIUM_RISK_THRESHOLD = float(RISK_THRESHOLDS["medium"])
HIGH_RISK_THRESHOLD = float(RISK_THRESHOLDS["high"])


# ============================================================
# PREDICT CHURN
# ============================================================

def predict_churn(customer_data: dict):

    df = pd.DataFrame([customer_data])

    probability = float(model.predict_proba(df)[0][1])

    probability_percentage = round(probability * 100, 2)

    if probability >= HIGH_RISK_THRESHOLD:
        risk_level = "High"
    elif probability >= MEDIUM_RISK_THRESHOLD:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "churn_probability": probability_percentage,
        "risk_level": risk_level,
    }


# ============================================================
# TEST PREDICTION
# ============================================================

if __name__ == "__main__":

    sample_customer = {
        "age": 30,
        "tenure_months": 6,
        "monthly_charges": 95.50,
        "total_charges": 573.00,
        "support_tickets": 6,
        "satisfaction_score": 4.0,
        "gender": "Male",
        "contract_type": "Month-to-month",
        "payment_method": "Electronic check",
        "internet_service": "Fiber optic",
    }

    result = predict_churn(sample_customer)

    print("\n==============================")
    print("CHURN PREDICTION")
    print("==============================")
    print(f"Churn Probability: {result['churn_probability']}%")
    print(f"Risk Level: {result['risk_level']}")
