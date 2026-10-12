from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
import csv
import io

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.customer import Customer
from app.models.prediction import ChurnPrediction
from app.models.user import User


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


def get_latest_predictions_query(db: Session):
    latest_prediction = (
        db.query(
            ChurnPrediction.customer_id,
            func.max(
                ChurnPrediction.predicted_at
            ).label("latest_prediction")
        )
        .group_by(
            ChurnPrediction.customer_id
        )
        .subquery()
    )

    return latest_prediction


# ============================================================
# CHURN SUMMARY REPORT
# ============================================================

@router.get("/churn-summary")
def get_churn_summary_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_customers = (
        db.query(func.count(Customer.id))
        .filter(Customer.is_active == True)
        .scalar()
    )

    churned_customers = (
        db.query(func.count(Customer.id))
        .filter(
            Customer.is_active == True,
            Customer.churned == True
        )
        .scalar()
    )

    non_churned_customers = (
        total_customers - churned_customers
    )

    churn_rate = (
        (churned_customers / total_customers) * 100
        if total_customers > 0
        else 0
    )

    return {
        "report": "Churn Summary",
        "total_customers": total_customers,
        "churned_customers": churned_customers,
        "non_churned_customers": non_churned_customers,
        "churn_rate": round(churn_rate, 2)
    }


# ============================================================
# CUSTOMER RISK REPORT
# ============================================================

@router.get("/customer-risk")
def get_customer_risk_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    latest_prediction = get_latest_predictions_query(db)

    results = (
        db.query(
            Customer.customer_id,
            Customer.full_name,
            Customer.email,
            Customer.monthly_charges,
            ChurnPrediction.churn_probability,
            ChurnPrediction.risk_level,
            ChurnPrediction.model_version,
            ChurnPrediction.predicted_at
        )
        .join(
            ChurnPrediction,
            Customer.id == ChurnPrediction.customer_id
        )
        .join(
            latest_prediction,
            (
                ChurnPrediction.customer_id
                == latest_prediction.c.customer_id
            )
            &
            (
                ChurnPrediction.predicted_at
                == latest_prediction.c.latest_prediction
            )
        )
        .filter(
            Customer.is_active == True
        )
        .order_by(
            ChurnPrediction.churn_probability.desc()
        )
        .all()
    )

    return [
        {
            "customer_id": row.customer_id,
            "customer_name": row.full_name,
            "email": row.email,
            "monthly_charges": round(
                float(row.monthly_charges),
                2
            ),
            "churn_probability": round(
                float(row.churn_probability) * 100,
                2
            ),
            "risk_level": row.risk_level,
            "model_version": row.model_version,
            "predicted_at": row.predicted_at
        }
        for row in results
    ]


# ============================================================
# REVENUE RISK REPORT
# ============================================================

@router.get("/revenue-risk")
def get_revenue_risk_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    latest_prediction = get_latest_predictions_query(db)

    results = (
        db.query(
            ChurnPrediction.risk_level,
            func.count(
                Customer.id
            ).label("customer_count"),
            func.sum(
                Customer.monthly_charges
            ).label("monthly_revenue")
        )
        .join(
            Customer,
            Customer.id == ChurnPrediction.customer_id
        )
        .join(
            latest_prediction,
            (
                ChurnPrediction.customer_id
                == latest_prediction.c.customer_id
            )
            &
            (
                ChurnPrediction.predicted_at
                == latest_prediction.c.latest_prediction
            )
        )
        .filter(
            Customer.is_active == True
        )
        .group_by(
            ChurnPrediction.risk_level
        )
        .all()
    )

    report = []

    for row in results:
        report.append({
            "risk_level": row.risk_level,
            "customer_count": row.customer_count,
            "monthly_revenue": round(
                float(row.monthly_revenue or 0),
                2
            )
        })

    return report


# ============================================================
# EXPORT CUSTOMER RISK REPORT
# ============================================================

@router.get("/export")
def export_customer_risk_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    latest_prediction = get_latest_predictions_query(db)

    results = (
        db.query(
            Customer.customer_id,
            Customer.full_name,
            Customer.email,
            Customer.monthly_charges,
            ChurnPrediction.churn_probability,
            ChurnPrediction.risk_level,
            ChurnPrediction.model_version,
            ChurnPrediction.predicted_at
        )
        .join(
            ChurnPrediction,
            Customer.id == ChurnPrediction.customer_id
        )
        .join(
            latest_prediction,
            (
                ChurnPrediction.customer_id
                == latest_prediction.c.customer_id
            )
            &
            (
                ChurnPrediction.predicted_at
                == latest_prediction.c.latest_prediction
            )
        )
        .filter(
            Customer.is_active == True
        )
        .order_by(
            ChurnPrediction.churn_probability.desc()
        )
        .all()
    )

    if not results:
        raise HTTPException(
            status_code=404,
            detail="No customer prediction data available"
        )

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Customer ID",
        "Customer Name",
        "Email",
        "Monthly Charges",
        "Churn Probability",
        "Risk Level",
        "Model Version",
        "Predicted At"
    ])

    for row in results:
        writer.writerow([
            row.customer_id,
            row.full_name,
            row.email,
            round(float(row.monthly_charges), 2),
            round(float(row.churn_probability) * 100, 2),
            row.risk_level,
            row.model_version,
            row.predicted_at
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition":
                "attachment; filename=customer_risk_report.csv"
        }
    )
