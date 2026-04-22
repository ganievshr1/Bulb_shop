from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_number = Column(String(50), unique=True, nullable=False)
    user_id = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    status = Column(String(50), default="new")
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    delivery_address = Column(Text, nullable=False)
    customer_name = Column(String(150), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    customer_email = Column(String(150))
    payment_method = Column(String(50))
    payment_status = Column(String(50), default="pending")
    comment = Column(Text)
    delivered_at = Column(TIMESTAMP, nullable=True)
    cancelled_at = Column(TIMESTAMP, nullable=True)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    status_history = relationship("OrderStatusHistory", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, nullable=False)
    product_name = Column(String(200), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    order = relationship("Order", back_populates="items")


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), nullable=False)
    changed_at = Column(TIMESTAMP, server_default=func.now())
    changed_by = Column(String(100))
    comment = Column(Text)

    order = relationship("Order", back_populates="status_history")