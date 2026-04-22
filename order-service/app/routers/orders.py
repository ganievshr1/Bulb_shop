from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime
import random
from decimal import Decimal

from app.database import get_db
from app import models, schemas

router = APIRouter(tags=["Orders"])


def generate_order_number():
    date_str = datetime.now().strftime("%Y%m%d")
    random_num = random.randint(1, 999999)
    return f"BLB-{date_str}-{random_num:06d}"


def serialize_order(order):
    return {
        "id": order.id,
        "order_number": order.order_number,
        "customer_name": order.customer_name,
        "customer_phone": order.customer_phone,
        "customer_email": order.customer_email,
        "delivery_address": order.delivery_address,
        "payment_method": order.payment_method,
        "status": order.status,
        "total_amount": float(order.total_amount) if order.total_amount else 0,
        "created_at": order.created_at.isoformat() if order.created_at else None
    }


def serialize_order_item(item):
    return {
        "id": item.id,
        "product_id": item.product_id,
        "product_name": item.product_name,
        "quantity": item.quantity,
        "unit_price": float(item.unit_price) if item.unit_price else 0,
        "total_price": float(item.total_price) if item.total_price else 0
    }


@router.post("/orders", status_code=status.HTTP_201_CREATED)
async def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    total_amount = Decimal("0.00")
    order_items = []

    for item in order.items:
        product_name = f"Product {item.product_id}"
        unit_price = Decimal("100.00")
        total_price = unit_price * item.quantity
        total_amount += total_price

        order_items.append({
            "product_id": item.product_id,
            "product_name": product_name,
            "quantity": item.quantity,
            "unit_price": unit_price,
            "total_price": total_price
        })

    order_number = generate_order_number()

    db_order = models.Order(
        order_number=order_number,
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        customer_email=order.customer_email,
        delivery_address=order.delivery_address,
        payment_method=order.payment_method,
        comment=order.comment,
        total_amount=total_amount,
        status="new"
    )
    db.add(db_order)
    db.flush()

    for item_data in order_items:
        db_item = models.OrderItem(
            order_id=db_order.id,
            **item_data
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_order)

    return {
        "success": True,
        "data": {
            "id": db_order.id,
            "order_number": db_order.order_number,
            "status": db_order.status,
            "total_amount": float(total_amount),
            "created_at": db_order.created_at.isoformat()
        }
    }


@router.get("/orders")
async def get_all_orders(
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1, le=100),
        db: Session = Depends(get_db)
):
    query = db.query(models.Order)
    total = query.count()
    offset = (page - 1) * limit
    orders = query.order_by(desc(models.Order.created_at)).offset(offset).limit(limit).all()

    orders_data = [serialize_order(o) for o in orders]

    return {
        "success": True,
        "data": orders_data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit if total > 0 else 1
        }
    }


@router.get("/orders/{order_id}")
async def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    items = db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id).all()
    order_dict = serialize_order(order)
    order_dict["items"] = [serialize_order_item(item) for item in items]
    return order_dict


@router.get("/orders/{order_id}/items")
async def get_order_items(order_id: int, db: Session = Depends(get_db)):
    items = db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id).all()
    return [serialize_order_item(item) for item in items]


@router.put("/orders/{order_id}/status")
async def update_order_status(
        order_id: int,
        status_update: dict,
        db: Session = Depends(get_db)
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    new_status = status_update.get("status")
    order.status = new_status

    if new_status == "delivered":
        order.delivered_at = datetime.now()
    elif new_status == "cancelled":
        order.cancelled_at = datetime.now()

    db.commit()

    return {
        "success": True,
        "data": {
            "id": order.id,
            "status": order.status,
            "updated_at": datetime.now().isoformat()
        }
    }


@router.put("/orders/{order_id}/cancel")
async def cancel_order(
        order_id: int,
        cancel_data: dict,
        db: Session = Depends(get_db)
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status in ["delivered", "cancelled"]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel order with status: {order.status}")

    order.status = "cancelled"
    order.cancelled_at = datetime.now()
    db.commit()

    return {
        "success": True,
        "data": {
            "id": order.id,
            "status": order.status,
            "cancelled_at": order.cancelled_at.isoformat()
        }
    }


@router.get("/orders/{order_id}/status-history")
async def get_order_status_history(order_id: int, db: Session = Depends(get_db)):
    history = db.query(models.OrderStatusHistory).filter(
        models.OrderStatusHistory.order_id == order_id
    ).order_by(models.OrderStatusHistory.changed_at).all()
    return [
        {
            "status": h.status,
            "changed_at": h.changed_at.isoformat() if h.changed_at else None,
            "changed_by": h.changed_by,
            "comment": h.comment
        }
        for h in history
    ]