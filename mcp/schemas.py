from pydantic import BaseModel, Field
from typing import Optional


class OrderRequest(BaseModel):
    order_id: str = Field(description="The unique identifier of the order.")


class OrderResponse(BaseModel):
    order_id: str
    status: str
    eta_days: Optional[int]