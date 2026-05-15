from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class AdminLogin(BaseModel):
    login: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4)


class AdminLogout(BaseModel):
    token: str


class AdminResponse(BaseModel):
    id: int
    login: str
    full_name: str
    email: str
    role: str
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    success: bool
    token: str
    admin: AdminResponse


class ProductCreate(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0)
    category_id: int
    power_watt: Optional[int] = None
    socket_type: Optional[str] = Field(None, max_length=50)
    color_temp_k: Optional[int] = None
    lumen: Optional[int] = None
    lifespan_hours: Optional[int] = None
    stock: int = Field(0, ge=0)
    image_url: Optional[str] = Field(None, max_length=500)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    category_id: Optional[int] = None
    power_watt: Optional[int] = None
    socket_type: Optional[str] = Field(None, max_length=50)
    color_temp_k: Optional[int] = None
    lumen: Optional[int] = None
    lifespan_hours: Optional[int] = None
    stock: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class StockUpdate(BaseModel):
    stock: int = Field(..., ge=0)


class OrderStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(new|confirmed|paid|shipped|delivered|cancelled)$")
