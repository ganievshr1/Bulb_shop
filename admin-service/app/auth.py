from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from . import models
from .config import settings
from .database import get_db

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if plain_password == "admin123" and hashed_password == "admin123":
        return True
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except (ValueError, TypeError):
        return plain_password == hashed_password


def get_password_hash(password: str) -> str:
    if password.startswith("$2b$") or password.startswith("$2a$"):
        return password
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if 'sub' in to_encode and isinstance(to_encode['sub'], int):
        to_encode['sub'] = str(to_encode['sub'])
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        print(f"Token decode error: {e}")
        return None


def is_token_blacklisted(db: Session, token: str) -> bool:
    return db.query(models.BlacklistedToken).filter(
        models.BlacklistedToken.token == token
    ).first() is not None


def blacklist_token(db: Session, token: str, expires_at: datetime):
    db_token = models.BlacklistedToken(token=token, expires_at=expires_at)
    db.add(db_token)
    db.commit()


async def get_current_admin(
    auth: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.Admin:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = auth.credentials
    print(f"Validating token: {token[:50]}...")
    
    if is_token_blacklisted(db, token):
        print("Token is blacklisted")
        raise credentials_exception
    
    payload = decode_token(token)
    if payload is None:
        print("Failed to decode token")
        raise credentials_exception
    
    admin_id = payload.get("sub")
    if admin_id is None:
        print("No sub in token")
        raise credentials_exception
    
    try:
        admin_id = int(admin_id)
    except (ValueError, TypeError):
        print(f"Invalid sub format: {admin_id}")
        raise credentials_exception
    
    admin = db.query(models.Admin).filter(
        models.Admin.id == admin_id,
        models.Admin.is_active == True
    ).first()
    
    if admin is None:
        print(f"Admin {admin_id} not found")
        raise credentials_exception
    
    print(f"Admin validated: {admin.login}")
    return admin
