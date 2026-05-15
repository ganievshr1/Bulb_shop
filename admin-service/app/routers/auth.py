from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app import models, schemas, auth
from app.config import settings
from app.utils import get_client_ip, get_user_agent
from app.services.audit_service import AuditService

router = APIRouter(prefix="/admin", tags=["Admin Auth"])


@router.post("/login", response_model=schemas.TokenResponse)
async def admin_login(
    login_data: schemas.AdminLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login for administrator"""
    admin = db.query(models.Admin).filter(
        models.Admin.login == login_data.login,
        models.Admin.is_active == True
    ).first()

    if not admin or not auth.verify_password(login_data.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login or password"
        )

    admin.last_login = datetime.utcnow()
    db.commit()

    access_token = auth.create_access_token(data={"sub": admin.id, "role": admin.role})

    await AuditService.log_action(
        db=db,
        admin_id=admin.id,
        action="LOGIN",
        entity_type="admin",
        entity_id=admin.id,
        new_value={"login": admin.login},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return schemas.TokenResponse(
        success=True,
        token=access_token,
        admin=schemas.AdminResponse.model_validate(admin)
    )


@router.post("/logout")
async def admin_logout(
    logout_data: schemas.AdminLogout,
    request: Request,
    current_admin: models.Admin = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Logout - blacklist the token"""
    payload = auth.decode_token(logout_data.token)
    if payload:
        expires_at = datetime.fromtimestamp(payload.get("exp"))
        auth.blacklist_token(db, logout_data.token, expires_at)

    await AuditService.log_action(
        db=db,
        admin_id=current_admin.id,
        action="LOGOUT",
        entity_type="admin",
        entity_id=current_admin.id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

    return {"success": True, "message": "Successfully logged out"}


@router.get("/me", response_model=schemas.AdminResponse)
async def get_current_admin_info(
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    """Get current admin info"""
    return current_admin
