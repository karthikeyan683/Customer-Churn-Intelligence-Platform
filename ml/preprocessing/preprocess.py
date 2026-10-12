from pathlib import Path

import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = BASE_DIR / "ml" / "data" / "customer_churn.csv"


NUMERICAL_FEATURES = [
    "age",
    "tenure_months",
    "monthly_charges",
    "total_charges",
    "support_tickets",
    "satisfaction_score"
]


CATEGORICAL_FEATURES = [
    "gender",
    "contract_type",
    "payment_method",
    "internet_service"
]


def load_dataset():
    df = pd.read_csv(DATA_PATH)

    return df


def create_preprocessor():
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numerical",
                StandardScaler(),
                NUMERICAL_FEATURES
            ),
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                CATEGORICAL_FEATURES
            )
        ]
    )

    return preprocessor


if __name__ == "__main__":

    df = load_dataset()

    print("Dataset loaded successfully! ✅")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\nFeatures:")
    print(
        NUMERICAL_FEATURES +
        CATEGORICAL_FEATURES
    )

    print("\nTarget:")
    print("churned")
