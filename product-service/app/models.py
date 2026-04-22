from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    power_watt = Column(Integer)
    socket_type = Column(String(50))
    color_temp_k = Column(Integer)
    lumen = Column(Integer)
    lifespan_hours = Column(Integer)
    stock = Column(Integer, nullable=False, default=0)
    image_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    category = relationship("Category", back_populates="products")
    attributes = relationship("ProductAttribute", back_populates="product")


class ProductAttribute(Base):
    __tablename__ = "product_attributes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    attribute_name = Column(String(100), nullable=False)
    attribute_value = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    product = relationship("Product", back_populates="attributes")