
from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "ml" / "data" / "customer_churn.csv"
MODEL_DIR = BASE_DIR / "ml" / "models"
MODEL_PATH = MODEL_DIR / "churn_model.joblib"
THRESHOLD_PATH = MODEL_DIR / "churn_thresholds.json"


# ============================================================
# FEATURES
# ============================================================

NUMERICAL_FEATURES = [
    "age",
    "tenure_months",
    "monthly_charges",
    "total_charges",
    "support_tickets",
    "satisfaction_score",
]

CATEGORICAL_FEATURES = [
    "gender",
    "contract_type",
    "payment_method",
    "internet_service",
]

FEATURES = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
TARGET = "churned"


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_STATE = 42
TEST_SIZE = 0.20
VALIDATION_SIZE = 0.20

# Minimum acceptable precision when selecting a threshold.
# This is a configurable business constraint, not a guarantee.
MIN_PRECISION = 0.40


def build_pipeline():
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numerical",
                StandardScaler(),
                NUMERICAL_FEATURES,
            ),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_FEATURES,
            ),
        ]
    )

    classifier = RandomForestClassifier(
        n_estimators=200,
        random_state=RANDOM_STATE,
        class_weight="balanced",
        n_jobs=-1,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", classifier),
        ]
    )


def select_threshold(y_true, probabilities):
    """Choose the validation threshold with the best F1 score,
    subject to a configurable minimum precision where possible.
    """

    results = []

    for threshold in [i / 100 for i in range(10, 91)]:
        predictions = (probabilities >= threshold).astype(int)

        precision = precision_score(
            y_true, predictions, zero_division=0
        )
        recall = recall_score(
            y_true, predictions, zero_division=0
        )
        f1 = f1_score(
            y_true, predictions, zero_division=0
        )

        results.append({
            "threshold": threshold,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        })

    eligible = [
        item for item in results
        if item["precision"] >= MIN_PRECISION
    ]

    candidates = eligible if eligible else results

    # Prefer the highest F1; on ties, prefer higher precision.
    best = max(
        candidates,
        key=lambda item: (item["f1"], item["precision"]),
    )

    return best, not bool(eligible)


def main():
    # --------------------------------------------------------
    # LOAD AND VALIDATE DATA
    # --------------------------------------------------------

    df = pd.read_csv(DATA_PATH)

    required_columns = FEATURES + [TARGET]
    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Dataset is missing required columns: {missing_columns}"
        )

    if df[required_columns].isna().any().any():
        raise ValueError(
            "Missing values found in model features or target."
        )

    target_values = set(df[TARGET].unique())
    if not target_values.issubset({True, False, 0, 1}):
        raise ValueError(
            f"Unexpected target values: {target_values}"
        )

    X = df[FEATURES]
    y = df[TARGET].astype(int)

    if y.nunique() != 2:
        raise ValueError(
            "Churn target must contain both classes."
        )

    print("=" * 60)
    print("CUSTOMER CHURN MODEL TRAINING")
    print("=" * 60)
    print(f"Dataset rows: {len(df)}")
    print(f"Churn rate: {y.mean():.2%}")

    # --------------------------------------------------------
    # SPLIT: 60% TRAIN, 20% VALIDATION, 20% TEST
    # --------------------------------------------------------

    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    validation_fraction = VALIDATION_SIZE / (1 - TEST_SIZE)

    X_train, X_validation, y_train, y_validation = (
        train_test_split(
            X_train_val,
            y_train_val,
            test_size=validation_fraction,
            random_state=RANDOM_STATE,
            stratify=y_train_val,
        )
    )

    print(f"Training rows:   {len(X_train)}")
    print(f"Validation rows: {len(X_validation)}")
    print(f"Test rows:       {len(X_test)}")

    # --------------------------------------------------------
    # TRAIN ON TRAINING DATA ONLY
    # --------------------------------------------------------

    pipeline = build_pipeline()

    print("\nTraining model...")
    pipeline.fit(X_train, y_train)
    print("Training completed.")

    # --------------------------------------------------------
    # SELECT THRESHOLD ON VALIDATION DATA
    # --------------------------------------------------------

    validation_probabilities = pipeline.predict_proba(
        X_validation
    )[:, 1]

    best, precision_constraint_unmet = select_threshold(
        y_validation,
        validation_probabilities,
    )

    threshold = best["threshold"]

    print("\nVALIDATION THRESHOLD")
    print("-" * 60)
    print(f"Selected threshold: {threshold:.2f}")
    print(f"Validation precision: {best['precision']:.4f}")
    print(f"Validation recall:    {best['recall']:.4f}")
    print(f"Validation F1:         {best['f1']:.4f}")

    if precision_constraint_unmet:
        print(
            "WARNING: No candidate met the minimum precision "
            f"constraint ({MIN_PRECISION:.2f}); selected the "
            "best available F1 candidate."
        )

    # --------------------------------------------------------
    # FINAL TEST EVALUATION
    # Do not use test results to select the threshold.
    # --------------------------------------------------------

    test_probabilities = pipeline.predict_proba(X_test)[:, 1]
    test_predictions = (
        test_probabilities >= threshold
    ).astype(int)

    print("\nHELD-OUT TEST PERFORMANCE")
    print("-" * 60)
    print(
        f"Accuracy:  {accuracy_score(y_test, test_predictions):.4f}"
    )
    print(
        f"Precision: {precision_score(y_test, test_predictions, zero_division=0):.4f}"
    )
    print(
        f"Recall:    {recall_score(y_test, test_predictions, zero_division=0):.4f}"
    )
    print(
        f"F1 Score:  {f1_score(y_test, test_predictions, zero_division=0):.4f}"
    )
    print(
        f"ROC-AUC:   {roc_auc_score(y_test, test_probabilities):.4f}"
    )

    matrix = confusion_matrix(
        y_test,
        test_predictions,
        labels=[0, 1],
    )

    print("\nConfusion matrix (rows=actual, columns=predicted):")
    print("                 Predicted stay  Predicted churn")
    print(f"Actual stay      {matrix[0, 0]:14d}  {matrix[0, 1]:15d}")
    print(f"Actual churn     {matrix[1, 0]:14d}  {matrix[1, 1]:15d}")

    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            test_predictions,
            labels=[0, 1],
            target_names=["Stay", "Churn"],
            zero_division=0,
        )
    )

    # --------------------------------------------------------
    # SAVE ARTIFACTS
    # Keep the model as a Pipeline for explain.py compatibility.
    # Save artifacts to temporary files before replacing targets.
    # --------------------------------------------------------

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    model_temp = MODEL_DIR / "churn_model.tmp.joblib"
    threshold_temp = MODEL_DIR / "churn_thresholds.tmp.json"

    metadata = {
        "threshold": threshold,
        "risk_thresholds": {
            "medium": threshold,
            "high": 0.70,
        },
        "selection_metric": "validation_f1",
        "minimum_precision_constraint": MIN_PRECISION,
        "validation_precision_constraint_unmet": precision_constraint_unmet,
        "validation_metrics": best,
        "test_metrics": {
            "accuracy": accuracy_score(y_test, test_predictions),
            "precision": precision_score(
                y_test, test_predictions, zero_division=0
            ),
            "recall": recall_score(
                y_test, test_predictions, zero_division=0
            ),
            "f1": f1_score(
                y_test, test_predictions, zero_division=0
            ),
            "roc_auc": roc_auc_score(y_test, test_probabilities),
        },
        "features": FEATURES,
        "random_state": RANDOM_STATE,
    }

    try:
        joblib.dump(pipeline, model_temp)

        with threshold_temp.open("w", encoding="utf-8") as file:
            json.dump(metadata, file, indent=2)

        # Preserve the original Pipeline artifact format.
        model_temp.replace(MODEL_PATH)
        threshold_temp.replace(THRESHOLD_PATH)

    finally:
        if model_temp.exists():
            model_temp.unlink()
        if threshold_temp.exists():
            threshold_temp.unlink()

    print("\nModel pipeline saved:", MODEL_PATH)
    print("Threshold metadata saved:", THRESHOLD_PATH)
    print("\nTraining and evaluation completed successfully.")


if __name__ == "__main__":
    main()
