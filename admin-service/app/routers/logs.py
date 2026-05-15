from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy.orm import Session

from app import auth, models
from app.database import get_db
from app.services.audit_service import AuditService

router = APIRouter(prefix="/admin", tags=["Admin Audit"])


@router.get("/logs")
async def get_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    admin_id: Optional[int] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    current_admin: models.Admin = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Get audit logs with filtering"""
    if admin_id and admin_id != current_admin.id and current_admin.role != "super_admin":
        raise HTTPException(status_code=403, detail="Only super admin can view other admins' logs")
    
    result = AuditService.get_logs(
        db=db,
        page=page,
        limit=limit,
        admin_id=admin_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        from_date=from_date,
        to_date=to_date
    )
    
    return {
        "success": True,
        "data": result["logs"],
        "pagination": result["pagination"]
    }


@router.get("/logs/entity/{entity_type}/{entity_id}")
async def get_entity_change_history(
    entity_type: str,
    entity_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_admin: models.Admin = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Get change history for specific entity"""
    result = AuditService.get_entity_history(
        db=db,
        entity_type=entity_type,
        entity_id=entity_id,
        page=page,
        limit=limit
    )
    
    return {
        "success": True,
        "data": result["logs"],
        "pagination": result["pagination"]
    }
