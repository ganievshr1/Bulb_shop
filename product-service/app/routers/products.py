from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal

from app.database import get_db
from app import schemas
from app.services.product_service import ProductService
from app.exceptions import ProductNotFoundError, InsufficientStockError

router = APIRouter(tags=["Products"])


@router.get("/products")
async def get_products(
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1, le=100),
        category_id: Optional[int] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        socket_type: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """Получить список товаров с фильтрацией"""
    products, total = ProductService.get_products(
        db, page, limit, category_id, min_price, max_price, socket_type
    )

    return {
        "success": True,
        "data": [schemas.ProductResponse.model_validate(p).model_dump() for p in products],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit if total > 0 else 1
        }
    }


@router.get("/products/search")
async def search_products(
        q: str = Query(..., min_length=1),
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1, le=100),
        db: Session = Depends(get_db)
):
    """Поиск товаров"""
    products, total = ProductService.search_products(db, q, page, limit)

    return {
        "success": True,
        "data": [schemas.ProductResponse.model_validate(p).model_dump() for p in products],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit if total > 0 else 1
        }
    }


@router.get("/products/{product_id}", response_model=schemas.ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Получить товар по ID"""
    try:
        product = ProductService.get_product(db, product_id)
        return product
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/products/{product_id}/stock")
async def get_product_stock(product_id: int, db: Session = Depends(get_db)):
    """Получить остаток товара"""
    try:
        product = ProductService.get_product(db, product_id)
        return {
            "product_id": product.id,
            "product_name": product.name,
            "stock": product.stock,
            "is_in_stock": product.stock > 0
        }
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/products", status_code=status.HTTP_201_CREATED, response_model=schemas.ProductResponse)
async def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Создать новый товар"""
    try:
        db_product = ProductService.create_product(db, product)
        return db_product
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/products/{product_id}", response_model=schemas.ProductResponse)
async def update_product(
        product_id: int,
        product_update: schemas.ProductUpdate,
        db: Session = Depends(get_db)
):
    """Обновить товар"""
    try:
        product = ProductService.update_product(db, product_id, product_update)
        return product
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/products/{product_id}/stock")
async def update_product_stock(
        product_id: int,
        stock_update: schemas.StockUpdate,
        db: Session = Depends(get_db)
):
    """Обновить остаток товара"""
    try:
        product = ProductService.get_product(db, product_id, active_only=False)
        product.stock = stock_update.stock
        db.commit()
        db.refresh(product)

        return {
            "product_id": product.id,
            "product_name": product.name,
            "stock": product.stock,
            "is_in_stock": product.stock > 0
        }
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Удалить товар (мягкое удаление)"""
    try:
        ProductService.delete_product(db, product_id)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))