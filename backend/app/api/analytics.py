
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.customer import Customer
from app.models.user import User
from app.models.prediction import ChurnPrediction


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


# ============================================================
# HELPER: LATEST PREDICTION FOR EACH CUSTOMER
# ============================================================

def get_latest_predictions_query(db: Session):
    return (
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


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Total active customers
    total_customers = (
        db.query(func.count(Customer.id))
        .filter(Customer.is_active == True)
        .scalar() or 0
    )

    # Customers marked as historically churned
    churned_customers = (
        db.query(func.count(Customer.id))
        .filter(
            Customer.is_active == True,
            Customer.churned == True
        )
        .scalar() or 0
    )

    active_customers = max(
        total_customers - churned_customers,
        0
    )

    # Actual historical churn rate
    churn_rate = (
        (churned_customers / total_customers) * 100
        if total_customers > 0 else 0
    )

    # Average monthly charges
    average_monthly_charges = (
        db.query(func.avg(Customer.monthly_charges))
        .filter(Customer.is_active == True)
        .scalar()
    )

    # Monthly revenue from active, non-churned customers
    total_monthly_revenue = (
        db.query(func.sum(Customer.monthly_charges))
        .filter(
            Customer.is_active == True,
            Customer.churned == False
        )
        .scalar()
    )

    # Latest prediction for each customer
    latest_prediction = get_latest_predictions_query(db)

    latest_prediction_filter = (
        (ChurnPrediction.customer_id
         == latest_prediction.c.customer_id)
        &
        (ChurnPrediction.predicted_at
         == latest_prediction.c.latest_prediction)
    )

    # Average predicted churn probability among customers
    # who have a latest prediction
    average_probability = (
        db.query(func.avg(ChurnPrediction.churn_probability))
        .join(
            Customer,
            Customer.id == ChurnPrediction.customer_id
        )
        .join(
            latest_prediction,
            latest_prediction_filter
        )
        .filter(Customer.is_active == True)
        .scalar()
    )

    # Monthly charges of customers classified High or Medium risk
    revenue_at_risk = (
        db.query(func.sum(Customer.monthly_charges))
        .join(
            ChurnPrediction,
            Customer.id == ChurnPrediction.customer_id
        )
        .join(
            latest_prediction,
            latest_prediction_filter
        )
        .filter(
            Customer.is_active == True,
            Customer.churned == False,
            ChurnPrediction.risk_level.in_(["High", "Medium"])
        )
        .scalar()
    )

    return {
        "total_customers": total_customers,
        "active_customers": active_customers,
        "churned_customers": churned_customers,
        "churn_rate": round(churn_rate, 2),
        "predicted_churn_rate": round(
            float(average_probability or 0) * 100,
            2
        ),
        "average_monthly_charges": round(
            float(average_monthly_charges or 0),
            2
        ),
        "total_monthly_revenue": round(
            float(total_monthly_revenue or 0),
            2
        ),
        "revenue_at_risk": round(
            float(revenue_at_risk or 0),
            2
        )
    }


# ============================================================
# CHURN BY CONTRACT
# ============================================================

@router.get("/churn-by-contract")
def get_churn_by_contract(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    results = (
        db.query(
            Customer.contract_type,
            func.count(Customer.id).label("total_customers"),
            func.sum(
                func.cast(Customer.churned, Integer)
            ).label("churned_customers")
        )
        .filter(Customer.is_active == True)
        .group_by(Customer.contract_type)
        .all()
    )

    response = []

    for row in results:
        total = row.total_customers or 0
        churned = row.churned_customers or 0

        churn_rate = (
            (churned / total) * 100
            if total > 0 else 0
        )

        response.append({
            "contract_type": row.contract_type or "Unknown",
            "total_customers": total,
            "churned_customers": churned,
            "churn_rate": round(churn_rate, 2)
        })

    return response


# ============================================================
# RISK DISTRIBUTION
# ============================================================

@router.get("/risk-distribution")
def get_risk_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    latest_prediction = get_latest_predictions_query(db)

    results = (
        db.query(
            ChurnPrediction.risk_level,
            func.count(
                func.distinct(ChurnPrediction.customer_id)
            ).label("customer_count")
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
            Customer.is_active == True,
            Customer.churned == False
        )
        .group_by(ChurnPrediction.risk_level)
        .all()
    )

    return [
        {
            "risk_level": row.risk_level,
            "customer_count": row.customer_count
        }
        for row in results
    ]


# ============================================================
# CHURN BY INTERNET SERVICE
# ============================================================

@router.get("/churn-by-internet")
def get_churn_by_internet(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    results = (
        db.query(
            Customer.internet_service,
            func.count(Customer.id).label("total_customers"),
            func.sum(
                func.cast(Customer.churned, Integer)
            ).label("churned_customers")
        )
        .filter(Customer.is_active == True)
        .group_by(Customer.internet_service)
        .all()
    )

    response = []

    for row in results:
        total = row.total_customers or 0
        churned = row.churned_customers or 0

        churn_rate = (
            (churned / total) * 100
            if total > 0 else 0
        )

        response.append({
            "internet_service": row.internet_service or "Unknown",
            "total_customers": total,
            "churned_customers": churned,
            "churn_rate": round(churn_rate, 2)
        })

    return response


# ============================================================
# HIGH-RISK CUSTOMERS
# ============================================================

@router.get("/high-risk-customers")
def get_high_risk_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    latest_prediction = get_latest_predictions_query(db)

    results = (
        db.query(
            Customer.customer_id,
            Customer.full_name,
            ChurnPrediction.churn_probability,
            ChurnPrediction.risk_level,
            Customer.monthly_charges,
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
            Customer.is_active == True,
            Customer.churned == False,
            ChurnPrediction.risk_level == "High"
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
            "churn_probability": round(
                float(row.churn_probability) * 100, 2
            ),
            "risk_level": row.risk_level,
            "monthly_charges": round(
                float(row.monthly_charges or 0), 2
            ),
            "predicted_at": row.predicted_at
        }
        for row in results
    ]


# ============================================================
# AT-RISK CUSTOMERS: HIGH + MEDIUM
# ============================================================

@router.get("/at-risk-customers")
def get_at_risk_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    latest_prediction = get_latest_predictions_query(db)

    results = (
        db.query(
            Customer.customer_id,
            Customer.full_name,
            ChurnPrediction.churn_probability,
            ChurnPrediction.risk_level,
            Customer.monthly_charges,
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
            Customer.is_active == True,
            Customer.churned == False,
            ChurnPrediction.risk_level.in_(["High", "Medium"])
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
            "churn_probability": round(
                float(row.churn_probability) * 100, 2
            ),
            "risk_level": row.risk_level,
            "monthly_charges": round(
                float(row.monthly_charges or 0), 2
            ),
            "predicted_at": row.predicted_at
        }
        for row in results
    ]


# ============================================================
# REVENUE AT RISK BY RISK LEVEL
# ============================================================

@router.get("/revenue-at-risk")
def get_revenue_at_risk(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    latest_prediction = get_latest_predictions_query(db)

    results = (
        db.query(
            ChurnPrediction.risk_level,
            func.sum(
                Customer.monthly_charges
            ).label("revenue_at_risk")
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
            Customer.is_active == True,
            Customer.churned == False,
            ChurnPrediction.risk_level.in_(["High", "Medium"])
        )
        .group_by(ChurnPrediction.risk_level)
        .all()
    )

    high_risk_revenue = 0.0
    medium_risk_revenue = 0.0

    for row in results:
        revenue = float(row.revenue_at_risk or 0)

        if row.risk_level == "High":
            high_risk_revenue = revenue
        elif row.risk_level == "Medium":
            medium_risk_revenue = revenue

    return {
        "high_risk_revenue": round(high_risk_revenue, 2),
        "medium_risk_revenue": round(medium_risk_revenue, 2),
        "total_revenue_at_risk": round(
            high_risk_revenue + medium_risk_revenue, 2
        )
    }


# ============================================================
# RISK SEGMENTS
# ============================================================

@router.get("/risk-segments")
def get_risk_segments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    latest_prediction = get_latest_predictions_query(db)

    results = (
        db.query(
            ChurnPrediction.risk_level,
            func.count(
                func.distinct(ChurnPrediction.customer_id)
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
            Customer.is_active == True,
            Customer.churned == False
        )
        .group_by(ChurnPrediction.risk_level)
        .all()
    )

    return [
        {
            "risk_level": row.risk_level,
            "customer_count": row.customer_count,
            "monthly_revenue": round(
                float(row.monthly_revenue or 0), 2
            )
        }
        for row in results
    ]
