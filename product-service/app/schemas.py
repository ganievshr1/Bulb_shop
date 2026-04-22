from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductAttributeBase(BaseModel):
    attribute_name: str
    attribute_value: str


class ProductAttributeResponse(ProductAttributeBase):
    id: int

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
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


class ProductCreate(ProductBase):
    pass


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


class ProductResponse(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    category_name: Optional[str] = None
    attributes: List[ProductAttributeResponse] = []

    class Config:
        from_attributes = True

class StockUpdate(BaseModel):
    stock: int = Field(..., ge=0)


class StockResponse(BaseModel):
    product_id: int
    product_name: str
    stock: int
    is_in_stock: bool