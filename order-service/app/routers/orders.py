from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app import schemas
from app.services.order_service import OrderService
from app.exceptions import OrderNotFoundError, InvalidOrderStatusError

router = APIRouter(tags=["Orders"])


@router.post("/orders", status_code=status.HTTP_201_CREATED)
async def create_order(
        order: schemas.OrderCreate,
        db: Session = Depends(get_db)
):
    """Создание нового заказа"""
    try:
        result = await OrderService.create_order(db, order)
        return {"success": True, "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/orders")
async def get_all_orders(
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1, le=100),
        status: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """Получение всех заказов (админская операция)"""
    orders, total = OrderService.get_orders(db, page, limit, status)

    return {
        "success": True,
        "data": [OrderService._serialize_order(o) for o in orders],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit if total > 0 else 1
        }
    }


@router.get("/orders/{order_id}")
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """Получение заказа по ID"""
    try:
        order = OrderService.get_order(db, order_id)
        items = OrderService.get_order_items(db, order_id)

        result = OrderService._serialize_order(order)
        result["items"] = [OrderService._serialize_order_item(item) for item in items]

        return result
    except OrderNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/orders/{order_id}/items")
async def get_order_items(order_id: int, db: Session = Depends(get_db)):
    """Получение позиций заказа"""
    try:
        items = OrderService.get_order_items(db, order_id)
        return [OrderService._serialize_order_item(item) for item in items]
    except OrderNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/orders/{order_id}/status")
async def update_order_status(
        order_id: int,
        status_update: dict,
        db: Session = Depends(get_db)
):
    """Обновление статуса заказа"""
    try:
        new_status = status_update.get("status")
        if not new_status:
            raise HTTPException(status_code=400, detail="Status is required")

        order = OrderService.update_order_status(
            db,
            order_id,
            new_status,
            changed_by=status_update.get("changed_by", "system"),
            comment=status_update.get("comment")
        )

        return {
            "success": True,
            "data": {
                "id": order.id,
                "status": order.status,
                "updated_at": datetime.now().isoformat()
            }
        }
    except OrderNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidOrderStatusError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/orders/{order_id}/status-history")
async def get_order_status_history(order_id: int, db: Session = Depends(get_db)):
    """Получение истории статусов заказа"""
    try:
        history = OrderService.get_order_status_history(db, order_id)
        return [
            {
                "status": h.status,
                "changed_at": h.changed_at.isoformat() if h.changed_at else None,
                "changed_by": h.changed_by,
                "comment": h.comment
            }
            for h in history
        ]
    except OrderNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Вспомогательные методы сериализации (можно вынести в отдельный модуль)
from datetime import datetime


@staticmethod
def _serialize_order(order):
    return {
        "id": order.id,
        "order_number": order.order_number,
        "customer_name": order.customer_name,
        "customer_phone": order.customer_phone,
        "customer_email": order.customer_email,
        "delivery_address": order.delivery_address,
        "payment_method": order.payment_method,
        "status": order.status,
        "payment_status": order.payment_status,
        "total_amount": float(order.total_amount) if order.total_amount else 0,
        "comment": order.comment,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "delivered_at": order.delivered_at.isoformat() if order.delivered_at else None,
        "cancelled_at": order.cancelled_at.isoformat() if order.cancelled_at else None
    }


@staticmethod
def _serialize_order_item(item):
    return {
        "id": item.id,
        "product_id": item.product_id,
        "product_name": item.product_name,
        "quantity": item.quantity,
        "unit_price": float(item.unit_price) if item.unit_price else 0,
        "total_price": float(item.total_price) if item.total_price else 0
    }


# Привязываем статические методы к классу
OrderService._serialize_order = _serialize_order
OrderService._serialize_order_item = _serialize_order_item