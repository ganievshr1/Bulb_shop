import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app import models
from app.auth import get_password_hash

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_admin.db"

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
    Base.metadata.create_all(bind=engine)

    # Create test admin
    db = TestingSessionLocal()
    admin = models.Admin(
        login="test_admin",
        password_hash=get_password_hash("test123"),
        full_name="Test Admin",
        email="test@example.com",
        role="super_admin",
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.close()

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def admin_token(client):
    response = client.post("/api/v1/admin/login", json={
        "login": "test_admin",
        "password": "test123"
    })
    return response.json().get("token")