from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from . import models
from .config import settings
from .database import get_db

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ✅ УДАЛЁН хардкод admin123
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля ТОЛЬКО через bcrypt"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except (ValueError, TypeError):
        return False  # ✅ Неправильный хеш → отказ


def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if 'sub' in to_encode and isinstance(to_encode['sub'], int):
        to_encode['sub'] = str(to_encode['sub'])

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})  # ✅ Добавлен iat
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Декодирование JWT токена"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": True}  # ✅ ЯВНАЯ проверка срока
        )
        return payload
    except JWTError as e:
        print(f"Token decode error: {e}")
        return None


def is_token_blacklisted(db: Session, token: str) -> bool:
    """Проверка, заблокирован ли токен"""
    return db.query(models.BlacklistedToken).filter(
        models.BlacklistedToken.token == token
    ).first() is not None


def blacklist_token(db: Session, token: str, expires_at: datetime):
    """Добавление токена в чёрный список"""
    db_token = models.BlacklistedToken(token=token, expires_at=expires_at)
    db.add(db_token)
    db.commit()


async def get_current_admin(
        auth: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
) -> models.Admin:
    """Получение текущего администратора из JWT токена"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = auth.credentials

    # ✅ Проверка blacklist
    if is_token_blacklisted(db, token):
        raise credentials_exception

    # ✅ Декодирование с проверкой срока
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    admin_id = payload.get("sub")
    if admin_id is None:
        raise credentials_exception

    try:
        admin_id = int(admin_id)
    except (ValueError, TypeError):
        raise credentials_exception

    # ✅ Проверка существования и активности админа
    admin = db.query(models.Admin).filter(
        models.Admin.id == admin_id,
        models.Admin.is_active == True
    ).first()

    if admin is None:
        raise credentials_exception

    return admin