from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    customer_name: str = Field(..., max_length=150)
    customer_phone: str = Field(..., max_length=20)
    customer_email: Optional[str] = Field(None, max_length=150)
    delivery_address: str
    payment_method: Optional[str] = Field(None, max_length=50)
    comment: Optional[str] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_name: str
    customer_phone: str
    customer_email: Optional[str]
    delivery_address: str
    payment_method: Optional[str]
    status: str
    payment_status: str
    total_amount: Decimal
    comment: Optional[str]
    created_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True