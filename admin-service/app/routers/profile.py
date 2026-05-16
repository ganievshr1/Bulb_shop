from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app import auth, models
from app.database import get_db

router = APIRouter(prefix="/admin", tags=["Admin Profile"])


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ChangePasswordResponse(BaseModel):
    success: bool
    message: str


@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(
    password_data: ChangePasswordRequest,
    current_admin: models.Admin = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    """Смена пароля администратора"""
    
    if not auth.verify_password(password_data.current_password, current_admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Текущий пароль введен неверно"
        )
    
    if len(password_data.new_password) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Новый пароль должен содержать минимум 4 символа"
        )
    
    current_admin.password_hash = auth.get_password_hash(password_data.new_password)
    db.commit()
    
    return ChangePasswordResponse(
        success=True,
        message="Пароль успешно изменен"
    )
