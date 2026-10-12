from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.customer import Customer
from app.models.prediction import ChurnPrediction
from app.models.user import User
from app.services.recommendation_service import generate_recommendations


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)


@router.post("/{customer_id}")
def get_customer_recommendations(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Find customer
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

    # Get latest prediction
    prediction = (
        db.query(ChurnPrediction)
        .filter(
            ChurnPrediction.customer_id == customer.id
        )
        .order_by(
            ChurnPrediction.predicted_at.desc()
        )
        .first()
    )

    if not prediction:
        raise HTTPException(
            status_code=404,
            detail="No prediction found for this customer"
        )

    # Generate recommendations
    recommendations = generate_recommendations(
        customer=customer,
        churn_probability=prediction.churn_probability,
        risk_level=prediction.risk_level
    )

    return {
        "customer_id": customer.customer_id,
        "customer_name": customer.full_name,
        "churn_probability": round(
            float(prediction.churn_probability) * 100,
            2
        ),
        "risk_level": prediction.risk_level,
        "recommendations": recommendations
    }
