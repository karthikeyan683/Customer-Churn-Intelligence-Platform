
import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.customer import Customer
from app.models.prediction import ChurnPrediction
from app.models.user import User
from app.services.audit_service import create_audit_log


BASE_DIR = Path(__file__).resolve().parents[3]

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from ml.prediction.predict import predict_churn
from ml.prediction.explain import explain_prediction


router = APIRouter(
    prefix="/predictions",
    tags=["Predictions"]
)

MODEL_VERSION = "1.0.0"


# ============================================================
# HELPER: CUSTOMER DATA FOR ML MODEL
# ============================================================

def get_customer_data(customer: Customer) -> dict:
    return {
        "age": customer.age,
        "tenure_months": customer.tenure_months,
        "monthly_charges": customer.monthly_charges,
        "total_charges": customer.total_charges,
        "support_tickets": customer.support_tickets,
        "satisfaction_score": customer.satisfaction_score,
        "gender": customer.gender,
        "contract_type": customer.contract_type,
        "payment_method": customer.payment_method,
        "internet_service": customer.internet_service
    }


# ============================================================
# BATCH PREDICTION
# POST /predictions/batch
# ============================================================

@router.post("/batch")
def batch_predict_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customers = (
        db.query(Customer)
        .filter(Customer.is_active == True)
        .all()
    )

    results = []

    try:
        for customer in customers:
            customer_data = get_customer_data(customer)
            result = predict_churn(customer_data)

            probability = float(
                result["churn_probability"] / 100
            )

            prediction = ChurnPrediction(
                customer_id=customer.id,
                churn_probability=probability,
                risk_level=result["risk_level"],
                model_version=MODEL_VERSION
            )

            db.add(prediction)

            results.append({
                "customer_id": customer.customer_id,
                "customer_name": customer.full_name,
                "churn_probability": float(
                    result["churn_probability"]
                ),
                "risk_level": result["risk_level"]
            })

        db.commit()

    except Exception:
        db.rollback()
        raise

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="BATCH_PREDICTION",
        endpoint="/predictions/batch",
        status="SUCCESS",
        details=(
            f"Batch prediction generated for "
            f"{len(results)} customers"
        )
    )
    db.commit()

    return {
        "total_predictions": len(results),
        "predictions": results
    }


# ============================================================
# LATEST SAVED PREDICTIONS — READ ONLY
# GET /predictions/latest
# ============================================================

@router.get("/latest")
def get_latest_predictions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rows = (
        db.query(Customer, ChurnPrediction)
        .join(
            ChurnPrediction,
            ChurnPrediction.customer_id == Customer.id
        )
        .filter(Customer.is_active == True)
        .order_by(
            Customer.id,
            ChurnPrediction.predicted_at.desc(),
            ChurnPrediction.id.desc()
        )
        .all()
    )

    latest_by_customer = {}

    for customer, prediction in rows:
        if customer.id not in latest_by_customer:
            latest_by_customer[customer.id] = {
                "customer_id": customer.customer_id,
                "customer_name": customer.full_name,
                "churn_probability": float(
                    prediction.churn_probability * 100
                ),
                "risk_level": prediction.risk_level,
                "model_version": prediction.model_version
            }

    results = list(latest_by_customer.values())

    return {
        "total_predictions": len(results),
        "predictions": results
    }


# ============================================================
# SINGLE CUSTOMER PREDICTION
# POST /predictions/{customer_id}
# ============================================================

@router.post("/{customer_id}")
def predict_customer_churn(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.customer_id == customer_id,
            Customer.is_active == True
        )
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    customer_data = get_customer_data(customer)
    result = predict_churn(customer_data)

    probability = float(
        result["churn_probability"] / 100
    )

    prediction = ChurnPrediction(
        customer_id=customer.id,
        churn_probability=probability,
        risk_level=result["risk_level"],
        model_version=MODEL_VERSION
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="PREDICTION_CREATED",
        endpoint=f"/predictions/{customer_id}",
        status="SUCCESS",
        details=(
            f"Churn prediction generated for "
            f"{customer.full_name}"
        )
    )
    db.commit()

    return {
        "customer_id": customer.customer_id,
        "churn_probability": float(
            result["churn_probability"]
        ),
        "risk_level": result["risk_level"],
        "model_version": MODEL_VERSION
    }


# ============================================================
# PREDICTION HISTORY
# GET /predictions/{customer_id}/history
# ============================================================

@router.get("/{customer_id}/history")
def get_prediction_history(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.customer_id == customer_id,
            Customer.is_active == True
        )
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    predictions = (
        db.query(ChurnPrediction)
        .filter(
            ChurnPrediction.customer_id == customer.id
        )
        .order_by(
            ChurnPrediction.predicted_at.desc(),
            ChurnPrediction.id.desc()
        )
        .all()
    )

    return [
        {
            "prediction_id": prediction.id,
            "customer_id": customer.customer_id,
            "churn_probability": float(
                prediction.churn_probability * 100
            ),
            "risk_level": prediction.risk_level,
            "model_version": prediction.model_version,
            "predicted_at": prediction.predicted_at
        }
        for prediction in predictions
    ]


# ============================================================
# SHAP EXPLANATION
# POST /predictions/{customer_id}/explain
# ============================================================

@router.post("/{customer_id}/explain")
def explain_customer_churn(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.customer_id == customer_id,
            Customer.is_active == True
        )
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    customer_data = get_customer_data(customer)
    explanations = explain_prediction(customer_data)

    return {
        "customer_id": customer.customer_id,
        "explanations": explanations
    }
