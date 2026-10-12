
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api.dependencies import (
    get_current_user,
    require_admin,
    require_analyst,
)
from app.db.session import get_db
from app.models.customer import Customer
from app.models.user import User
from app.schemas.customer import CustomerCreate, CustomerResponse


router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


# ============================================================
# CREATE CUSTOMER - ADMIN / ANALYST
# ============================================================

@router.post(
    "/",
    response_model=CustomerResponse,
    status_code=201,
)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    # Check duplicate customer ID
    existing_id = (
        db.query(Customer)
        .filter(
            Customer.customer_id == customer_data.customer_id
        )
        .first()
    )

    if existing_id:
        raise HTTPException(
            status_code=409,
            detail="Customer ID already exists",
        )

    # Check duplicate email
    existing_email = (
        db.query(Customer)
        .filter(
            Customer.email == customer_data.email
        )
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=409,
            detail="Customer email already exists",
        )

    customer = Customer(**customer_data.model_dump())

    try:
        db.add(customer)
        db.commit()
        db.refresh(customer)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Customer ID or email already exists",
        )

    return customer


# ============================================================
# GET CUSTOMERS - AUTHENTICATED USERS
# SEARCH, FILTER, PAGINATION
# ============================================================

@router.get(
    "/",
    response_model=list[CustomerResponse],
)
def get_customers(
    search: str | None = None,
    contract_type: str | None = None,
    churned: bool | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Customer).filter(
        Customer.is_active.is_(True)
    )

    # Search by customer ID, name, or email
    if search:
        search_pattern = f"%{search}%"

        query = query.filter(
            (Customer.customer_id.ilike(search_pattern))
            | (Customer.full_name.ilike(search_pattern))
            | (Customer.email.ilike(search_pattern))
        )

    # Filter by contract type
    if contract_type:
        query = query.filter(
            Customer.contract_type == contract_type
        )

    # Filter by churn status
    if churned is not None:
        query = query.filter(
            Customer.churned == churned
        )

    offset = (page - 1) * page_size

    customers = (
        query
        .order_by(Customer.id.asc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return customers


# ============================================================
# GET SINGLE CUSTOMER - AUTHENTICATED USERS
# ============================================================

@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
)
def get_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.customer_id == customer_id,
            Customer.is_active.is_(True),
        )
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return customer


# ============================================================
# UPDATE CUSTOMER - ADMIN / ANALYST
# ============================================================

@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
)
def update_customer(
    customer_id: str,
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.customer_id == customer_id,
            Customer.is_active.is_(True),
        )
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    # Prevent assigning another customer's ID
    duplicate_id = (
        db.query(Customer)
        .filter(
            Customer.id != customer.id,
            Customer.customer_id == customer_data.customer_id,
        )
        .first()
    )

    if duplicate_id:
        raise HTTPException(
            status_code=409,
            detail="Customer ID already exists",
        )

    # Prevent assigning another customer's email
    duplicate_email = (
        db.query(Customer)
        .filter(
            Customer.id != customer.id,
            Customer.email == customer_data.email,
        )
        .first()
    )

    if duplicate_email:
        raise HTTPException(
            status_code=409,
            detail="Customer email already exists",
        )

    # Apply updates
    for field, value in customer_data.model_dump().items():
        setattr(customer, field, value)

    try:
        db.commit()
        db.refresh(customer)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Customer ID or email already exists",
        )

    return customer


# ============================================================
# SOFT DELETE CUSTOMER - ADMIN ONLY
# ============================================================

@router.delete(
    "/{customer_id}",
)
def delete_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    customer = (
        db.query(Customer)
        .filter(
            Customer.customer_id == customer_id,
            Customer.is_active.is_(True),
        )
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    # Preserve the record; only deactivate it
    customer.is_active = False

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Unable to deactivate customer",
        )

    return {
        "message": "Customer deactivated successfully",
        "customer_id": customer.customer_id,
    }
