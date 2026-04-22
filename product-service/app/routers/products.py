from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal

from app.database import get_db
from app import models, schemas

router = APIRouter(tags=["Products"])


@router.get("/products", response_model=dict)
async def get_products(
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1, le=100),
        category_id: Optional[int] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        socket_type: Optional[str] = None,
        db: Session = Depends(get_db)
):
    query = db.query(models.Product).filter(models.Product.is_active == True)

    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    if min_price:
        query = query.filter(models.Product.price >= min_price)
    if max_price:
        query = query.filter(models.Product.price <= max_price)
    if socket_type:
        query = query.filter(models.Product.socket_type == socket_type)

    total = query.count()
    offset = (page - 1) * limit
    products = query.offset(offset).limit(limit).all()

    products_data = [schemas.ProductResponse.model_validate(p).model_dump() for p in products]

    return {
        "success": True,
        "data": products_data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit if total > 0 else 1
        }
    }


# ВАЖНО: эти маршруты должны быть ПЕРЕД /products/{product_id}
@router.get("/products/search", response_model=dict)
async def search_products(
        q: str = Query(..., min_length=1),
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1, le=100),
        db: Session = Depends(get_db)
):
    query = db.query(models.Product).filter(
        models.Product.is_active == True,
        (models.Product.name.ilike(f"%{q}%")) | (models.Product.description.ilike(f"%{q}%"))
    )

    total = query.count()
    offset = (page - 1) * limit
    products = query.offset(offset).limit(limit).all()

    products_data = [schemas.ProductResponse.model_validate(p).model_dump() for p in products]

    return {
        "success": True,
        "data": products_data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit if total > 0 else 1
        }
    }


@router.get("/products/filter", response_model=dict)
async def filter_products(
        power_from: Optional[int] = Query(None, ge=0),
        power_to: Optional[int] = Query(None, ge=0),
        socket_type: Optional[str] = None,
        color_temp_from: Optional[int] = None,
        color_temp_to: Optional[int] = None,
        price_from: Optional[Decimal] = None,
        price_to: Optional[Decimal] = None,
        db: Session = Depends(get_db)
):
    query = db.query(models.Product).filter(models.Product.is_active == True)

    if power_from:
        query = query.filter(models.Product.power_watt >= power_from)
    if power_to:
        query = query.filter(models.Product.power_watt <= power_to)
    if socket_type:
        query = query.filter(models.Product.socket_type == socket_type)
    if color_temp_from:
        query = query.filter(models.Product.color_temp_k >= color_temp_from)
    if color_temp_to:
        query = query.filter(models.Product.color_temp_k <= color_temp_to)
    if price_from:
        query = query.filter(models.Product.price >= price_from)
    if price_to:
        query = query.filter(models.Product.price <= price_to)

    products = query.all()
    products_data = [schemas.ProductResponse.model_validate(p).model_dump() for p in products]

    return {
        "success": True,
        "data": products_data,
        "count": len(products_data)
    }


@router.get("/products/category/{category_id}", response_model=dict)
async def get_products_by_category(
        category_id: int,
        db: Session = Depends(get_db)
):
    category = db.query(models.Category).filter(
        models.Category.id == category_id,
        models.Category.is_active == True
    ).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    products = db.query(models.Product).filter(
        models.Product.category_id == category_id,
        models.Product.is_active == True
    ).all()

    products_data = [schemas.ProductResponse.model_validate(p).model_dump() for p in products]

    return {
        "success": True,
        "data": products_data,
        "category": {
            "id": category.id,
            "name": category.name
        }
    }


@router.get("/products/{product_id}", response_model=schemas.ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(
        models.Product.id == product_id,
        models.Product.is_active == True
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.get("/products/{product_id}/stock", response_model=dict)
async def get_product_stock(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(
        models.Product.id == product_id,
        models.Product.is_active == True
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "product_id": product.id,
        "product_name": product.name,
        "stock": product.stock,
        "is_in_stock": product.stock > 0
    }


@router.put("/products/{product_id}/stock", response_model=dict)
async def update_product_stock(
        product_id: int,
        stock_update: schemas.StockUpdate,
        db: Session = Depends(get_db)
):
    """Обновить остаток товара на складе (административная операция)"""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.stock = stock_update.stock
    db.commit()
    db.refresh(product)

    return {
        "product_id": product.id,
        "product_name": product.name,
        "stock": product.stock,
        "is_in_stock": product.stock > 0,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None
    }


@router.post("/products", status_code=status.HTTP_201_CREATED, response_model=schemas.ProductResponse)
async def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.put("/products/{product_id}", response_model=schemas.ProductResponse)
async def update_product(product_id: int, product_update: schemas.ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.is_active = False
    db.commit()