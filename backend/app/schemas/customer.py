from datetime import date

from pydantic import BaseModel, EmailStr, ConfigDict


class CustomerCreate(BaseModel):
    customer_id: str
    full_name: str
    email: EmailStr
    gender: str | None = None
    age: int | None = None
    tenure_months: int = 0
    monthly_charges: float = 0.0
    total_charges: float = 0.0
    contract_type: str | None = None
    payment_method: str | None = None
    internet_service: str | None = None
    support_tickets: int = 0
    satisfaction_score: float | None = None
    churned: bool = False
    signup_date: date | None = None


class CustomerResponse(CustomerCreate):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
