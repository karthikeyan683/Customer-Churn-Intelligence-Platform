from pydantic import BaseModel


class PredictionResponse(BaseModel):
    customer_id: str
    churn_probability: float
    risk_level: str
    model_version: str
