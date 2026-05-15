from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import Optional
from decimal import Decimal
from sqlalchemy.orm import Session

from app import auth, schemas, models
from app.services.product_service import ProductService
from app.services.audit_service import AuditService
from app.database import get_db
from app.utils import get_client_ip, get_user_agent

router = APIRouter(prefix="/admin", tags=["Admin Products"])


@router.get("/products")
async def get_all_products(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    socket_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_admin: models.Admin = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all products (including inactive)"""
    result = await ProductService.get_all_products(
        page=page,
        limit=limit,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        socket_type=socket_type,
        is_active=is_active
    )
    
    await AuditService.log_action(
        db=db,
        admin_id=current_admin.id,
        action="VIEW",
        entity_type="product",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        new_value={"page": page, "limit": limit}
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
    result = await ProductService.get_product(product_id)
    
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


@router.post("/products", status_code=201)
async def create_product(
    product: schemas.ProductCreate,
    request: Request,
    current_admin: models.Admin = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Create new product"""
    result = await ProductService.create_product(product.model_dump())
    
    await AuditService.log_action(
        db=db,
        admin_id=current_admin.id,
        action="CREATE",
        entity_type="product",
        entity_id=result.get("id") if result else None,
        new_value=product.model_dump(),
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
    """Update product"""
    old_product = await ProductService.get_product(product_id)
    result = await ProductService.update_product(product_id, product_update.model_dump(exclude_unset=True))
    
    await AuditService.log_action(
        db=db,
        admin_id=current_admin.id,
        action="UPDATE",
        entity_type="product",
        entity_id=product_id,
        old_value=old_product,
        new_value=product_update.model_dump(exclude_unset=True),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return result


@router.delete("/products/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    request: Request,
    current_admin: models.Admin = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete product (soft delete)"""
    old_product = await ProductService.get_product(product_id)
    await ProductService.delete_product(product_id)
    
    await AuditService.log_action(
        db=db,
        admin_id=current_admin.id,
        action="DELETE",
        entity_type="product",
        entity_id=product_id,
        old_value=old_product,
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
    """Update product stock"""
    old_product = await ProductService.get_product(product_id)
    old_stock = old_product.get("stock") if old_product else None
    
    result = await ProductService.update_product_stock(product_id, stock_update.stock)
    
    await AuditService.log_action(
        db=db,
        admin_id=current_admin.id,
        action="UPDATE",
        entity_type="product",
        entity_id=product_id,
        old_value={"stock": old_stock},
        new_value={"stock": stock_update.stock},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return result
