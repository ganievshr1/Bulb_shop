from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

from . import models
from .database import engine, SessionLocal
from .config import settings
from .routers import auth_router, products_router, orders_router, logs_router
from .auth import get_password_hash


def init_admin_user():
    """Initialize default admin user if not exists"""
    db = SessionLocal()
    try:
        admin = db.query(models.Admin).filter(
            models.Admin.login == settings.ADMIN_LOGIN
        ).first()

        if not admin:
            admin = models.Admin(
                login=settings.ADMIN_LOGIN,
                password_hash=get_password_hash(settings.ADMIN_PASSWORD),
                full_name=settings.ADMIN_FULL_NAME,
                email=settings.ADMIN_EMAIL,
                role="super_admin",
                is_active=True
            )
            db.add(admin)
            db.commit()
            print(f"✅ Default admin user created: {settings.ADMIN_LOGIN}")
        else:
            print(f"✅ Admin user already exists: {settings.ADMIN_LOGIN}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Create database tables
    models.Base.metadata.create_all(bind=engine)

    # Initialize default admin user
    init_admin_user()

    print(f"🚀 {settings.SERVICE_NAME} started on port {settings.SERVICE_PORT}")
    yield
    print(f"👋 {settings.SERVICE_NAME} shutting down")


app = FastAPI(
    title="Admin Service",
    description="Микросервис панели управления интернет-магазином лампочек",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")
app.include_router(logs_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.SERVICE_NAME}


@app.get("/")
async def root():
    return {
        "message": "Admin Service is running",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/v1/admin/*",
            "products": "/api/v1/admin/products",
            "orders": "/api/v1/admin/orders",
            "logs": "/api/v1/admin/logs"
        }
    }