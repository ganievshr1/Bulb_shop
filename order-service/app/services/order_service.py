import httpx
from datetime import datetime
from sqlalchemy.orm import Session
from decimal import Decimal
from .. import models, schemas
from ..config import settings


def generate_order_number():
    """Generate unique order number: BLB-YYYYMMDD-XXXXXX"""
    from datetime import datetime
    import random

    date_str = datetime.now().strftime("%Y%m%d")
    random_num = random.randint(1, 999999)
    return f"BLB-{date_str}-{random_num:06d}"


async def validate_and_reserve_stock(items: list):
    """Validate stock and reserve items via Product Service"""
    async with httpx.AsyncClient() as client:
        for item in items:
            # Check stock
            stock_response = await client.get(
                f"{settings.PRODUCT_SERVICE_URL}/products/{item['product_id']}/stock"
            )
            if stock_response.status_code != 200:
                raise ValueError(f"Product {item['product_id']} not found")

            stock_data = stock_response.json()
            if stock_data["data"]["stock"] < item["quantity"]:
                product_name = stock_data["data"]["product_name"]
                raise ValueError(f"Insufficient stock for product: {product_name}")


async def get_product_info(product_id: int):
    """Get product info from Product Service"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.PRODUCT_SERVICE_URL}/products/{product_id}"
        )
        if response.status_code != 200:
            raise ValueError(f"Product {product_id} not found")
        return response.json()["data"]


async def update_product_stock(product_id: int, new_stock: int):
    """Update product stock via Product Service"""
    async with httpx.AsyncClient() as client:
        await client.put(
            f"{settings.PRODUCT_SERVICE_URL}/products/{product_id}/stock",
            json={"stock": new_stock}
        )


def add_status_history(db: Session, order_id: int, status: str, changed_by: str, comment: str = None):
    """Add entry to order status history"""
    history = models.OrderStatusHistory(
        order_id=order_id,
        status=status,
        changed_by=changed_by,
        comment=comment
    )
    db.add(history)
    db.commit()


async def create_order(db: Session, order_data: schemas.OrderCreate):
    """Create new order"""
    # Validate stock
    await validate_and_reserve_stock([item.model_dump() for item in order_data.items])

    # Get product info and calculate total
    total_amount = Decimal("0.00")
    order_items = []

    for item in order_data.items:
        product_info = await get_product_info(item.product_id)

        unit_price = Decimal(str(product_info["price"]))
        total_price = unit_price * item.quantity
        total_amount += total_price

        order_items.append({
            "product_id": item.product_id,
            "product_name": product_info["name"],
            "quantity": item.quantity,
            "unit_price": unit_price,
            "total_price": total_price
        })

    # Create order
    order_number = generate_order_number()

    db_order = models.Order(
        order_number=order_number,
        customer_name=order_data.customer_name,
        customer_phone=order_data.customer_phone,
        customer_email=order_data.customer_email,
        delivery_address=order_data.delivery_address,
        payment_method=order_data.payment_method,
        comment=order_data.comment,
        total_amount=total_amount,
        status="new"
    )
    db.add(db_order)
    db.flush()

    # Add order items
    for item_data in order_items:
        db_item = models.OrderItem(
            order_id=db_order.id,
            **item_data
        )
        db.add(db_item)

    # Add status history
    add_status_history(db, db_order.id, "new", "system", "Order created")

    db.commit()
    db.refresh(db_order)

    # Update stock in Product Service (decrease)
    for item in order_data.items:
        product_info = await get_product_info(item.product_id)
        new_stock = product_info["stock"] - item.quantity
        await update_product_stock(item.product_id, new_stock)

    return {
        "id": db_order.id,
        "order_number": db_order.order_number,
        "status": db_order.status,
        "total_amount": float(total_amount),
        "created_at": db_order.created_at.isoformat()
    }