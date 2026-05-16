from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from typing import Optional
from decimal import Decimal
from sqlalchemy.orm import Session
import re

from app import auth, schemas, models
from app.services.product_service import ProductService
from app.services.audit_service import AuditService
from app.database import get_db
from app.utils import get_client_ip, get_user_agent

router = APIRouter(prefix="/admin", tags=["Admin Products"])


def validate_socket_type(socket_type: Optional[str]) -> Optional[str]:
    """Валидация типа цоколя (только буквы, цифры, дефис)"""
    if socket_type and not re.match(r'^[A-Za-z0-9\-]+$', socket_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid socket_type format. Use only letters, numbers and hyphens"
        )
    return socket_type


def validate_product_name(name: Optional[str]) -> Optional[str]:
    """Валидация названия товара"""
    if name and len(name) > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product name must be less than 200 characters"
        )
    return name


@router.get("/products")
async def get_all_products(
        request: Request,
        page: int = Query(1, ge=1, le=1000),  # ✅ Ограничение сверху
        limit: int = Query(20, ge=1, le=100),
        category_id: Optional[int] = Query(None, ge=1),  # ✅ Только положительные
        min_price: Optional[Decimal] = Query(None, ge=0),
        max_price: Optional[Decimal] = Query(None, ge=0),
        socket_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        current_admin: models.Admin = Depends(auth.get_current_admin),
        db: Session = Depends(get_db)
):
    """Get all products (including inactive) with validation"""

    # ✅ Валидация входных параметров
    if min_price and max_price and min_price > max_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_price cannot be greater than max_price"
        )

    socket_type = validate_socket_type(socket_type)

    result = await ProductService.get_all_products(
        page=page,
        limit=limit,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        socket_type=socket_type,
        is_active=is_active
    )

    # ✅ Логирование без чувствительных данных
    await AuditService.log_action(
        db=db,
        admin_id=current_admin.id,
        action="VIEW_LIST",
        entity_type="product",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        new_value={
            "page": page,
            "limit": limit,
            "filters": {
                "category_id": category_id,
                "price_range": f"{min_price}-{max_price}" if min_price or max_price else None,
                "socket_type": socket_type,
                "is_active": is_active
            }
        }
    )

    return result


@router.get("/products/{product_id}")
async def get_product(
        product_id: int,
        request: Request,
        current_admin: models.Admin = Depends(auth.get_current_admin),
        db: Session = Depends(get_db)
):
    """Get product by ID"""

    # ✅ Валидация ID
    if product_id < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID"
        )

    result = await ProductService.get_product(product_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found"
        )

    await AuditService.log_action(
        db=db,
        admin_id=current_admin.id,
        action="VIEW",
        entity_type="product",
        entity_id=product_id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return result


@router.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product(
        product: schemas.ProductCreate,
        request: Request,
        current_admin: models.Admin = Depends(auth.get_current_admin),
        db: Session = Depends(get_db)
):
    """Create new product with validation"""

    # ✅ Дополнительная валидация перед отправкой
    validate_product_name(product.name)

    if product.socket_type:
        validate_socket_type(product.socket_type)

    if product.price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price must be greater than 0"
        )

    # ✅ Очистка данных от None значений
    product_data = product.model_dump(exclude_none=True)

    result = await ProductService.create_product(product_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product"
        )

    product_id = result.get("id")

    await AuditService.log_action(
        db=db,
        admin_id=current_admin.id,
        action="CREATE",
        entity_type="product",
        entity_id=product_id,
        new_value={
            "name": product.name,
            "price": str(product.price),
            "category_id": product.category_id
        },
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return result


@router.put("/products/{product_id}")
async def update_product(
        product_id: int,
        product_update: schemas.ProductUpdate,
        request: Request,
        current_admin: models.Admin = Depends(auth.get_current_admin),
        db: Session = Depends(get_db)
):
    """Update product with validation"""

    # ✅ Валидация ID
    if product_id < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID"
        )

    # ✅ Проверка существования продукта
    old_product = await ProductService.get_product(product_id)
    if not old_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found"
        )

    # ✅ Валидация обновляемых полей
    update_data = product_update.model_dump(exclude_unset=True)

    if 'name' in update_data:
        validate_product_name(update_data['name'])

    if 'socket_type' in update_data and update_data['socket_type']:
        validate_socket_type(update_data['socket_type'])

    if 'price' in update_data and update_data['price'] <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price must be greater than 0"
        )

    result = await ProductService.update_product(product_id, update_data)

    # ✅ Логирование только изменённых полей
    changes = {}
    for key in update_data:
        old_val = old_product.get(key)
        new_val = update_data[key]
        if str(old_val) != str(new_val):
            changes[key] = {"old": str(old_val), "new": str(new_val)}

    await AuditService.log_action(
        db=db,
        admin_id=current_admin.id,
        action="UPDATE",
        entity_type="product",
        entity_id=product_id,
        old_value={"changed_fields": list(changes.keys())},
        new_value=changes,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return result


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
        product_id: int,
        request: Request,
        current_admin: models.Admin = Depends(auth.get_current_admin),
        db: Session = Depends(get_db)
):
    """Delete product (soft delete)"""

    # ✅ Валидация ID
    if product_id < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID"
        )

    # ✅ Проверка существования продукта
    old_product = await ProductService.get_product(product_id)
    if not old_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found"
        )

    await ProductService.delete_product(product_id)

    await AuditService.log_action(
        db=db,
        admin_id=current_admin.id,
        action="DELETE",
        entity_type="product",
        entity_id=product_id,
        old_value={"name": old_product.get("name"), "id": product_id},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return None


@router.put("/products/{product_id}/stock")
async def update_product_stock(
        product_id: int,
        stock_update: schemas.StockUpdate,
        request: Request,
        current_admin: models.Admin = Depends(auth.get_current_admin),
        db: Session = Depends(get_db)
):
    """Update product stock with validation"""

    # ✅ Валидация ID
    if product_id < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID"
        )

    # ✅ Дополнительная валидация количества
    if stock_update.stock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock cannot be negative"
        )

    if stock_update.stock > 1000000:  # ✅ Разумный лимит
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock value too high (max: 1,000,000)"
        )

    # ✅ Проверка существования продукта
    old_product = await ProductService.get_product(product_id)
    if not old_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found"
        )

    old_stock = old_product.get("stock")

    result = await ProductService.update_product_stock(product_id, stock_update.stock)

    await AuditService.log_action(
        db=db,
        admin_id=current_admin.id,
        action="UPDATE_STOCK",
        entity_type="product",
        entity_id=product_id,
        old_value={"stock": old_stock},
        new_value={"stock": stock_update.stock},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return result