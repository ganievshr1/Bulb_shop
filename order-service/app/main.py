from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import orders
from .config import settings

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Order Service",
    description="Микросервис управления заказами",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ВАЖНО: добавляем префикс /api/v1
app.include_router(orders.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.SERVICE_NAME}

@app.get("/")
async def root():
    return {"message": "Order Service is running"}