import random
from datetime import date, timedelta

import pandas as pd


random.seed(42)

records = []

contract_types = [
    "Month-to-month",
    "One year",
    "Two year"
]

payment_methods = [
    "Credit card",
    "Bank transfer",
    "Electronic check",
    "Mailed check"
]

internet_services = [
    "Fiber optic",
    "DSL",
    "No internet"
]

genders = [
    "Male",
    "Female"
]


for i in range(1, 1001):

    age = random.randint(18, 75)

    tenure_months = random.randint(1, 72)

    monthly_charges = round(
        random.uniform(25, 120),
        2
    )

    total_charges = round(
        monthly_charges * tenure_months *
        random.uniform(0.85, 1.15),
        2
    )

    contract_type = random.choice(contract_types)

    payment_method = random.choice(payment_methods)

    internet_service = random.choice(
        internet_services
    )

    support_tickets = random.randint(0, 8)

    satisfaction_score = round(
        random.uniform(1, 10),
        1
    )

    gender = random.choice(genders)

    signup_date = (
        date.today()
        - timedelta(days=tenure_months * 30)
    )

    # Churn probability logic
    churn_score = 0

    if contract_type == "Month-to-month":
        churn_score += 3

    if monthly_charges > 80:
        churn_score += 2

    if tenure_months < 12:
        churn_score += 2

    if support_tickets >= 4:
        churn_score += 2

    if satisfaction_score <= 5:
        churn_score += 3

    if payment_method == "Electronic check":
        churn_score += 1

    if internet_service == "Fiber optic":
        churn_score += 1

    churn_probability = min(
        churn_score / 15,
        0.95
    )

    churned = (
        random.random() < churn_probability
    )

    records.append({
        "customer_id": f"CUS-{i:04d}",
        "gender": gender,
        "age": age,
        "tenure_months": tenure_months,
        "monthly_charges": monthly_charges,
        "total_charges": total_charges,
        "contract_type": contract_type,
        "payment_method": payment_method,
        "internet_service": internet_service,
        "support_tickets": support_tickets,
        "satisfaction_score": satisfaction_score,
        "churned": churned,
        "signup_date": signup_date
    })


df = pd.DataFrame(records)

output_path = "ml/data/customer_churn.csv"

df.to_csv(
    output_path,
    index=False
)

print("Dataset created successfully! ✅")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print(f"Saved to: {output_path}")
print()
print("Churn distribution:")
print(df["churned"].value_counts())
