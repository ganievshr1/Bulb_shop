from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app import models, schemas, auth
from app.config import settings
from app.utils import get_client_ip, get_user_agent
from app.services.audit_service import AuditService

router = APIRouter(prefix="/admin", tags=["Admin Auth"])

# ✅ Rate limiting: 5 попыток в минуту
limiter = Limiter(key_func=get_remote_address)


@router.post("/login", response_model=schemas.TokenResponse)
@limiter.limit("5/minute")  # ✅ Защита от брутфорса
async def admin_login(
        request: Request,
        login_data: schemas.AdminLogin,
        db: Session = Depends(get_db)
):
    """Login for administrator"""

    # ✅ Защита от перебора: поиск пользователя
    admin = db.query(models.Admin).filter(
        models.Admin.login == login_data.login
    ).first()

    # ✅ Не показываем, существует ли пользователь
    if not admin:
        # Имитируем проверку хеша для защиты от тайминг-атак
        auth.get_password_hash(login_data.password)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login or password"
        )

    # ✅ Проверка блокировки
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )

    # ✅ Проверка пароля
    if not auth.verify_password(login_data.password, admin.password_hash):
        # Логирование неудачной попытки
        await AuditService.log_action(
            db=db,
            admin_id=admin.id,
            action="LOGIN_FAILED",
            entity_type="admin",
            entity_id=admin.id,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login or password"
        )

    # Успешный вход
    admin.last_login = datetime.utcnow()
    db.commit()

    access_token = auth.create_access_token(data={"sub": admin.id, "role": admin.role})

    await AuditService.log_action(
        db=db,
        admin_id=admin.id,
        action="LOGIN",
        entity_type="admin",
        entity_id=admin.id,
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