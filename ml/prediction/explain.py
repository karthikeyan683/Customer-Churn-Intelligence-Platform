from pathlib import Path

import joblib
import pandas as pd
import shap


# ============================================================
# PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "ml"
    / "models"
    / "churn_model.joblib"
)


# ============================================================
# LOAD MODEL
# ============================================================

model = joblib.load(MODEL_PATH)


# ============================================================
# EXPLAIN PREDICTION
# ============================================================

def explain_prediction(customer_data: dict):

    df = pd.DataFrame([customer_data])

    # Get preprocessing pipeline
    preprocessor = model.named_steps["preprocessor"]

    # Get trained classifier
    classifier = model.named_steps["model"]

    # Transform customer data
    transformed_data = preprocessor.transform(df)

    # Get feature names
    feature_names = (
        preprocessor
        .get_feature_names_out()
    )

    # SHAP explainer
    explainer = shap.TreeExplainer(
        classifier
    )

    shap_values = explainer.shap_values(
        transformed_data
    )

    # ========================================================
    # HANDLE DIFFERENT SHAP OUTPUT FORMATS
    # ========================================================

    if isinstance(shap_values, list):

        # Older SHAP versions
        values = shap_values[1][0]

    else:

        # Newer SHAP versions
        shap_array = shap_values

        if len(shap_array.shape) == 3:

            # Shape example:
            # (samples, features, classes)

            values = shap_array[0, :, 1]

        elif len(shap_array.shape) == 2:

            # Shape example:
            # (samples, features)

            values = shap_array[0]

        else:

            values = shap_array

    # Convert to 1-dimensional array
    values = values.reshape(-1)

    # Make sure lengths match
    feature_names = list(feature_names)

    if len(feature_names) != len(values):
        raise ValueError(
            f"Feature count ({len(feature_names)}) "
            f"does not match SHAP value count "
            f"({len(values)})"
        )

    # ========================================================
    # CREATE EXPLANATION TABLE
    # ========================================================

    explanation = pd.DataFrame({
        "feature": feature_names,
        "impact": values
    })

    # Absolute impact
    explanation["absolute_impact"] = (
        explanation["impact"].abs()
    )

    # Sort by strongest factors
    explanation = explanation.sort_values(
        "absolute_impact",
        ascending=False
    )

    # Top 10 factors
    top_factors = explanation.head(10)

    return [
        {
            "feature": row["feature"],
            "impact": round(
                float(row["impact"]),
                4
            ),
            "direction": (
                "increases_churn"
                if row["impact"] > 0
                else "decreases_churn"
            )
        }
        for _, row in top_factors.iterrows()
    ]


# ============================================================
# TEST
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
        "internet_service": "Fiber optic"
    }

    result = explain_prediction(
        sample_customer
    )

    print("\n==============================")
    print("SHAP EXPLANATION")
    print("==============================")

    for factor in result:

        print(
            f"{factor['feature']} | "
            f"Impact: {factor['impact']} | "
            f"{factor['direction']}"
        )
