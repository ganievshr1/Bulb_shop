from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import Optional
from sqlalchemy.orm import Session

from app import auth, schemas, models
from app.services.order_service import OrderService
from app.services.audit_service import AuditService
from app.database import get_db
from app.utils import get_client_ip, get_user_agent

router = APIRouter(prefix="/admin", tags=["Admin Orders"])


@router.get("/orders")
async def get_all_orders(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    current_admin: models.Admin = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all orders with filtering"""
    result = await OrderService.get_all_orders(page=page, limit=limit, status=status)
    
    await AuditService.log_action(
        db=db,
        admin_id=current_admin.id,
        action="VIEW",
        entity_type="order",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        new_value={"page": page, "limit": limit, "status": status}
    )
    
    return result


@router.get("/orders/{order_id}")
async def get_order(
    order_id: int,
    request: Request,
    current_admin: models.Admin = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Get order by ID"""
    result = await OrderService.get_order(order_id)
    
    await AuditService.log_action(
        db=db,
        admin_id=current_admin.id,
        action="VIEW",
        entity_type="order",
        entity_id=order_id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return result


@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    status_update: schemas.OrderStatusUpdate,
    request: Request,
    current_admin: models.Admin = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Update order status"""
    old_order = await OrderService.get_order(order_id)
    old_status = old_order.get("status") if old_order else None
    
    result = await OrderService.update_order_status(order_id, status_update.status)
    
    await AuditService.log_action(
        db=db,
        admin_id=current_admin.id,
        action="UPDATE",
        entity_type="order",
        entity_id=order_id,
        old_value={"status": old_status},
        new_value={"status": status_update.status},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return result
