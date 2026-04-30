from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple
import random

from app import models, schemas
from app.clients.product_client import product_client
from app.exceptions import OrderNotFoundError, InvalidOrderStatusError


class OrderService:
    """Сервис для работы с заказами"""

    @staticmethod
    def generate_order_number() -> str:
        """Сгенерировать уникальный номер заказа"""
        date_str = datetime.now().strftime("%Y%m%d")
        random_num = random.randint(1, 999999)
        return f"BLB-{date_str}-{random_num:06d}"

    @staticmethod
    def get_order(db: Session, order_id: int) -> models.Order:
        """Получить заказ по ID"""
        order = db.query(models.Order).filter(models.Order.id == order_id).first()
        if not order:
            raise OrderNotFoundError(f"Order {order_id} not found")
        return order

    @staticmethod
    def get_order_by_number(db: Session, order_number: str) -> models.Order:
        """Получить заказ по номеру"""
        order = db.query(models.Order).filter(
            models.Order.order_number == order_number
        ).first()
        if not order:
            raise OrderNotFoundError(f"Order {order_number} not found")
        return order

    @staticmethod
    def get_orders(
            db: Session,
            page: int = 1,
            limit: int = 20,
            status: Optional[str] = None,
            user_id: Optional[int] = None
    ) -> Tuple[List[models.Order], int]:
        """Получить список заказов с пагинацией"""
        query = db.query(models.Order)

        if status:
            query = query.filter(models.Order.status == status)
        if user_id:
            query = query.filter(models.Order.user_id == user_id)

        query = query.order_by(models.Order.created_at.desc())

        total = query.count()
        offset = (page - 1) * limit
        orders = query.offset(offset).limit(limit).all()

        return orders, total

    @staticmethod
    async def create_order(db: Session, order_data: schemas.OrderCreate) -> dict:
        """Создать новый заказ"""
        # 1. Валидация товаров через Product Service
        items_data = await product_client.validate_products(
            [item.model_dump() for item in order_data.items]
        )

        # 2. Расчет общей суммы
        total_amount = sum(item["total_price"] for item in items_data)

        # 3. Создание заказа
        order_number = OrderService.generate_order_number()

        db_order = models.Order(
            order_number=order_number,
            customer_name=order_data.customer_name,
            customer_phone=order_data.customer_phone,
            customer_email=order_data.customer_email,
            delivery_address=order_data.delivery_address,
            payment_method=order_data.payment_method,
            comment=order_data.comment,
            total_amount=total_amount,
            status="new",
            payment_status="pending"
        )
        db.add(db_order)
        db.flush()

        # 4. Добавление позиций заказа
        for item_data in items_data:
            db_item = models.OrderItem(
                order_id=db_order.id,
                **item_data
            )
            db.add(db_item)

        # 5. Добавление записи в историю
        history = models.OrderStatusHistory(
            order_id=db_order.id,
            status="new",
            changed_by="system",
            comment="Заказ создан"
        )
        db.add(history)

        db.commit()
        db.refresh(db_order)

        # 6. Обновление остатков в Product Service
        for item in order_data.items:
            product = await product_client.get_product(item.product_id)
            new_stock = product["stock"] - item.quantity
            await product_client.update_product_stock(item.product_id, new_stock)

        return {
            "id": db_order.id,
            "order_number": db_order.order_number,
            "status": db_order.status,
            "total_amount": float(total_amount),
            "created_at": db_order.created_at.isoformat() if db_order.created_at else None
        }

    @staticmethod
    def update_order_status(
            db: Session,
            order_id: int,
            new_status: str,
            changed_by: str = "system",
            comment: str = None
    ) -> models.Order:
        """Обновить статус заказа"""
        order = OrderService.get_order(db, order_id)

        # Валидация перехода статуса
        allowed_transitions = {
            "new": ["confirmed", "cancelled"],
            "confirmed": ["paid", "cancelled"],
            "paid": ["shipped", "cancelled"],
            "shipped": ["delivered", "cancelled"],
            "delivered": [],
            "cancelled": []
        }

        if new_status not in allowed_transitions.get(order.status, []):
            raise InvalidOrderStatusError(
                f"Cannot change order status from {order.status} to {new_status}"
            )

        old_status = order.status
        order.status = new_status

        # Установка дат
        if new_status == "delivered":
            order.delivered_at = datetime.now()
        elif new_status == "cancelled":
            order.cancelled_at = datetime.now()

        # Добавление записи в историю
        history = models.OrderStatusHistory(
            order_id=order.id,
            status=new_status,
            changed_by=changed_by,
            comment=comment or f"Статус изменен с {old_status} на {new_status}"
        )
        db.add(history)

        db.commit()
        db.refresh(order)

        return order

    @staticmethod
    def get_order_items(db: Session, order_id: int) -> List[models.OrderItem]:
        """Получить позиции заказа"""
        order = OrderService.get_order(db, order_id)
        return order.items

    @staticmethod
    def get_order_status_history(db: Session, order_id: int) -> List[models.OrderStatusHistory]:
        """Получить историю статусов заказа"""
        order = OrderService.get_order(db, order_id)
        return order.status_history