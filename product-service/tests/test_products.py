import pytest
from app import models


def test_get_products(client, sample_product):
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1


def test_get_product_by_id(client, sample_product):
    response = client.get(f"/api/v1/products/{sample_product.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_product.id
    assert data["name"] == sample_product.name


def test_get_product_not_found(client):
    response = client.get("/api/v1/products/99999")
    assert response.status_code == 404


def test_get_product_stock(client, sample_product):
    response = client.get(f"/api/v1/products/{sample_product.id}/stock")
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == sample_product.id
    assert data["stock"] == sample_product.stock
    assert data["is_in_stock"] is True


def test_search_products(client, sample_product):
    response = client.get("/api/v1/products/search?q=LED")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_filter_products(client, sample_product):
    response = client.get("/api/v1/products/filter?power_from=5&power_to=10")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_create_product(client, sample_category):
    product_data = {
        "name": "Test LED Bulb",
        "description": "Test Description",
        "price": 199.99,
        "category_id": sample_category.id,
        "power_watt": 9,
        "socket_type": "E27",
        "stock": 50
    }
    response = client.post("/api/v1/products", json=product_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == product_data["name"]


def test_update_product(client, sample_product):
    update_data = {"price": 229.99, "stock": 80}
    response = client.put(f"/api/v1/products/{sample_product.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert float(data["price"]) == 229.99
    assert data["stock"] == 80


def test_update_stock(client, sample_product):
    stock_data = {"stock": 75}
    response = client.put(f"/api/v1/products/{sample_product.id}/stock", json=stock_data)
    assert response.status_code == 200
    data = response.json()
    assert data["stock"] == 75


def test_delete_product(client, sample_product):
    response = client.delete(f"/api/v1/products/{sample_product.id}")
    assert response.status_code == 204

    # Verify product is deactivated
    get_response = client.get(f"/api/v1/products/{sample_product.id}")
    assert get_response.status_code == 404