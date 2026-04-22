import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime
from decimal import Decimal

from app.main import app
from app.database import Base, get_db
from app import models
from app.services import order_service

# Test database (SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_order.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Создание тестового клиента"""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Создание сессии БД для тестов"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def sample_order(db_session):
    """Создание тестового заказа"""
    order = models.Order(
        order_number="BLB-20260101-000001",
        user_id=1,
        customer_name="Иван Иванов",
        customer_phone="+79161234567",
        customer_email="ivan@example.com",
        delivery_address="г. Москва, ул. Тверская, д. 10, кв. 5",
        payment_method="card",
        status="new",
        payment_status="pending",
        total_amount=Decimal("697.00"),
        comment="Позвонить за час до доставки"
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order


@pytest.fixture
def sample_order_with_items(db_session, sample_order):
    """Создание тестового заказа с позициями"""
    # Создаем позиции заказа
    items = [
        models.OrderItem(
            order_id=sample_order.id,
            product_id=1,
            product_name="LED E27 7W 2700K",
            quantity=2,
            unit_price=Decimal("249.00"),
            total_price=Decimal("498.00")
        ),
        models.OrderItem(
            order_id=sample_order.id,
            product_id=3,
            product_name="LED GU10 5W 6500K",
            quantity=1,
            unit_price=Decimal("199.00"),
            total_price=Decimal("199.00")
        )
    ]
    for item in items:
        db_session.add(item)

    # Добавляем историю статусов
    history = models.OrderStatusHistory(
        order_id=sample_order.id,
        status="new",
        changed_by="system",
        comment="Заказ создан"
    )
    db_session.add(history)

    db_session.commit()

    return sample_order


@pytest.fixture
def sample_shipped_order(db_session):
    """Создание тестового заказа со статусом shipped"""
    order = models.Order(
        order_number="BLB-20260101-000002",
        customer_name="Петр Петров",
        customer_phone="+79261234567",
        customer_email="petr@example.com",
        delivery_address="г. Санкт-Петербург, Невский пр., д. 25",
        payment_method="cash",
        status="shipped",
        payment_status="paid",
        total_amount=Decimal("399.00")
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order


@pytest.fixture
def sample_delivered_order(db_session):
    """Создание тестового заказа со статусом delivered"""
    order = models.Order(
        order_number="BLB-20260101-000003",
        customer_name="Анна Сидорова",
        customer_phone="+79361234567",
        customer_email="anna@example.com",
        delivery_address="г. Новосибирск, ул. Ленина, д. 5",
        payment_method="card",
        status="delivered",
        payment_status="paid",
        total_amount=Decimal("599.00"),
        delivered_at=datetime.now()
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order


@pytest.fixture
def sample_cancelled_order(db_session):
    """Создание тестового заказа со статусом cancelled"""
    order = models.Order(
        order_number="BLB-20260101-000004",
        customer_name="Михаил Смирнов",
        customer_phone="+79461234567",
        customer_email="mikhail@example.com",
        delivery_address="г. Екатеринбург, ул. Малышева, д. 30",
        payment_method="card",
        status="cancelled",
        payment_status="pending",
        total_amount=Decimal("249.00"),
        cancelled_at=datetime.now()
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order


@pytest.fixture
def sample_order_history(db_session, sample_order):
    """Создание истории статусов заказа"""
    history_entries = [
        models.OrderStatusHistory(
            order_id=sample_order.id,
            status="new",
            changed_by="system",
            changed_at=datetime(2026, 1, 1, 10, 0, 0),
            comment="Заказ создан"
        ),
        models.OrderStatusHistory(
            order_id=sample_order.id,
            status="confirmed",
            changed_by="admin",
            changed_at=datetime(2026, 1, 1, 11, 0, 0),
            comment="Заказ подтвержден"
        ),
        models.OrderStatusHistory(
            order_id=sample_order.id,
            status="shipped",
            changed_by="admin",
            changed_at=datetime(2026, 1, 1, 14, 0, 0),
            comment=None
        )
    ]
    for entry in history_entries:
        db_session.add(entry)
    db_session.commit()
    return history_entries


@pytest.fixture
def mock_product_service_response(monkeypatch):
    """Mock ответов от Product Service"""

    async def mock_get_product_info(product_id):
        products = {
            1: {"id": 1, "name": "LED E27 7W 2700K", "price": 249.00, "stock": 100},
            2: {"id": 2, "name": "LED E27 9W 4000K", "price": 299.00, "stock": 85},
            3: {"id": 3, "name": "LED GU10 5W 6500K", "price": 199.00, "stock": 120},
        }
        if product_id in products:
            return products[product_id]
        raise ValueError(f"Product {product_id} not found")

    async def mock_validate_stock(items):
        for item in items:
            if item["product_id"] == 1 and item["quantity"] > 100:
                raise ValueError("Insufficient stock")
        return True

    async def mock_update_stock(product_id, new_stock):
        return True

    monkeypatch.setattr(order_service, "get_product_info", mock_get_product_info)
    monkeypatch.setattr(order_service, "validate_and_reserve_stock", mock_validate_stock)
    monkeypatch.setattr(order_service, "update_product_stock", mock_update_stock)

    return True