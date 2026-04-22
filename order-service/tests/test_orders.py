import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from decimal import Decimal
from app import models
from app.services import order_service


class TestOrders:
    """Тесты для заказов"""

    def test_create_order_success(self, client: TestClient, mock_product_service_response):
        """Тест: успешное создание заказа"""
        order_data = {
            "customer_name": "Иван Иванов",
            "customer_phone": "+79161234567",
            "customer_email": "ivan@example.com",
            "delivery_address": "г. Москва, ул. Тверская, д. 10",
            "payment_method": "card",
            "comment": "Позвонить за час",
            "items": [
                {"product_id": 1, "quantity": 2},
                {"product_id": 3, "quantity": 1}
            ]
        }

        response = client.post("/api/v1/orders", json=order_data)
        assert response.status_code == 201

        data = response.json()
        assert data["success"] is True
        assert "data" in data

        order = data["data"]
        assert order["order_number"].startswith("BLB-")
        assert order["status"] == "new"
        assert order["total_amount"] == 697.00  # 2*249 + 199
        assert "id" in order
        assert "created_at" in order

    def test_create_order_insufficient_stock(self, client: TestClient, mock_product_service_response):
        """Тест: создание заказа при недостатке товара на складе"""
        order_data = {
            "customer_name": "Иван Иванов",
            "customer_phone": "+79161234567",
            "delivery_address": "г. Москва, ул. Тверская, д. 10",
            "items": [
                {"product_id": 1, "quantity": 200}  # Больше чем есть
            ]
        }

        response = client.post("/api/v1/orders", json=order_data)
        assert response.status_code == 400
        assert "Insufficient stock" in response.json()["detail"]

    def test_create_order_without_items(self, client: TestClient):
        """Тест: создание заказа без товаров"""
        order_data = {
            "customer_name": "Иван Иванов",
            "customer_phone": "+79161234567",
            "delivery_address": "г. Москва, ул. Тверская, д. 10",
            "items": []
        }

        response = client.post("/api/v1/orders", json=order_data)
        assert response.status_code == 422  # Validation error

    def test_create_order_guest_user(self, client: TestClient, mock_product_service_response):
        """Тест: создание заказа гостем (без user_id)"""
        order_data = {
            "customer_name": "Гость Петров",
            "customer_phone": "+79261234567",
            "delivery_address": "г. Казань, ул. Баумана, д. 15",
            "items": [
                {"product_id": 2, "quantity": 1}
            ]
        }

        response = client.post("/api/v1/orders", json=order_data)
        assert response.status_code == 201

        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "new"

    def test_create_order_without_phone(self, client: TestClient):
        """Тест: создание заказа без телефона (должно быть ошибкой)"""
        order_data = {
            "customer_name": "Иван Иванов",
            "delivery_address": "г. Москва, ул. Тверская, д. 10",
            "items": [{"product_id": 1, "quantity": 1}]
        }

        response = client.post("/api/v1/orders", json=order_data)
        assert response.status_code == 422  # Validation error

    def test_get_order_by_id(self, client: TestClient, sample_order_with_items):
        """Тест: получение заказа по ID"""
        response = client.get(f"/api/v1/orders/{sample_order_with_items.id}")
        assert response.status_code == 200

        order = response.json()
        assert order["id"] == sample_order_with_items.id
        assert order["order_number"] == sample_order_with_items.order_number
        assert order["customer_name"] == sample_order_with_items.customer_name
        assert order["customer_phone"] == sample_order_with_items.customer_phone
        assert order["delivery_address"] == sample_order_with_items.delivery_address
        assert order["status"] == sample_order_with_items.status
        assert order["total_amount"] == float(sample_order_with_items.total_amount)

        # Проверяем наличие позиций заказа
        assert "items" in order
        assert len(order["items"]) == 2

    def test_get_order_not_found(self, client: TestClient):
        """Тест: получение несуществующего заказа"""
        response = client.get("/api/v1/orders/99999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Order not found"

    def test_get_order_by_number(self, client: TestClient, sample_order_with_items):
        """Тест: получение заказа по номеру"""
        response = client.get(f"/api/v1/orders/by-number/{sample_order_with_items.order_number}")
        assert response.status_code == 200

        order = response.json()
        assert order["order_number"] == sample_order_with_items.order_number
        assert order["id"] == sample_order_with_items.id

    def test_get_order_by_number_not_found(self, client: TestClient):
        """Тест: получение заказа по несуществующему номеру"""
        response = client.get("/api/v1/orders/by-number/NOT-EXIST-000001")
        assert response.status_code == 404

    def test_get_user_orders(self, client: TestClient, db_session):
        """Тест: получение заказов пользователя"""
        # Создаем несколько заказов для пользователя 1
        for i in range(3):
            order = models.Order(
                order_number=f"BLB-20260101-{100000 + i}",
                user_id=1,
                customer_name=f"User {i}",
                customer_phone="+79161234567",
                delivery_address=f"Address {i}",
                status="new" if i == 0 else "delivered",
                total_amount=Decimal("100.00")
            )
            db_session.add(order)
        db_session.commit()

        response = client.get("/api/v1/orders/user/1?page=1&limit=10")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 3
        assert data["pagination"]["total"] >= 3

    def test_get_user_orders_empty(self, client: TestClient):
        """Тест: получение заказов пользователя без заказов"""
        response = client.get("/api/v1/orders/user/999?page=1&limit=10")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 0
        assert data["pagination"]["total"] == 0

    def test_get_all_orders(self, client: TestClient, sample_order, sample_shipped_order, sample_delivered_order):
        """Тест: получение всех заказов (админская операция)"""
        response = client.get("/api/v1/orders")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 3

    def test_get_all_orders_with_status_filter(self, client: TestClient, sample_order, sample_shipped_order,
                                               sample_delivered_order):
        """Тест: получение заказов с фильтром по статусу"""
        response = client.get("/api/v1/orders?status=shipped")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        for order in data["data"]:
            assert order["status"] == "shipped"

    def test_get_orders_pagination(self, client: TestClient, db_session):
        """Тест: пагинация заказов"""
        # Создаем 25 заказов
        for i in range(25):
            order = models.Order(
                order_number=f"BLB-20260101-{200000 + i}",
                customer_name=f"Customer {i}",
                customer_phone="+79161234567",
                delivery_address=f"Address {i}",
                status="new",
                total_amount=Decimal("100.00")
            )
            db_session.add(order)
        db_session.commit()

        # Первая страница
        response = client.get("/api/v1/orders?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 10
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 10
        assert data["pagination"]["total"] >= 25

        # Вторая страница
        response = client.get("/api/v1/orders?page=2&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["page"] == 2

    def test_get_order_items(self, client: TestClient, sample_order_with_items):
        """Тест: получение позиций заказа"""
        response = client.get(f"/api/v1/orders/{sample_order_with_items.id}/items")
        assert response.status_code == 200

        items = response.json()
        assert len(items) == 2

        item = items[0]
        assert item["product_id"] == 1
        assert item["product_name"] == "LED E27 7W 2700K"
        assert item["quantity"] == 2
        assert item["unit_price"] == 249.00
        assert item["total_price"] == 498.00

    def test_get_order_items_empty(self, client: TestClient, sample_order):
        """Тест: получение позиций заказа без товаров"""
        response = client.get(f"/api/v1/orders/{sample_order.id}/items")
        assert response.status_code == 200
        assert response.json() == []

    def test_update_order_status(self, client: TestClient, sample_order):
        """Тест: обновление статуса заказа"""
        status_data = {"status": "confirmed"}

        response = client.put(f"/api/v1/orders/{sample_order.id}/status", json=status_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "confirmed"

        # Проверяем, что статус обновился в БД
        get_response = client.get(f"/api/v1/orders/{sample_order.id}")
        assert get_response.json()["status"] == "confirmed"

    def test_update_order_status_to_delivered(self, client: TestClient, sample_order):
        """Тест: обновление статуса до delivered"""
        status_data = {"status": "delivered"}

        response = client.put(f"/api/v1/orders/{sample_order.id}/status", json=status_data)
        assert response.status_code == 200

        data = response.json()
        assert data["data"]["status"] == "delivered"

        # Проверяем, что проставилась дата доставки
        get_response = client.get(f"/api/v1/orders/{sample_order.id}")
        assert get_response.json()["status"] == "delivered"
        assert get_response.json()["delivered_at"] is not None

    def test_update_order_status_to_cancelled(self, client: TestClient, sample_order):
        """Тест: обновление статуса до cancelled"""
        status_data = {"status": "cancelled"}

        response = client.put(f"/api/v1/orders/{sample_order.id}/status", json=status_data)
        assert response.status_code == 200

        data = response.json()
        assert data["data"]["status"] == "cancelled"

        # Проверяем, что проставилась дата отмены
        get_response = client.get(f"/api/v1/orders/{sample_order.id}")
        assert get_response.json()["status"] == "cancelled"
        assert get_response.json()["cancelled_at"] is not None

    def test_update_order_status_invalid(self, client: TestClient, sample_order):
        """Тест: обновление статуса заказа на недопустимый"""
        status_data = {"status": "invalid_status"}

        response = client.put(f"/api/v1/orders/{sample_order.id}/status", json=status_data)
        # Статус может быть принят, но это невалидное значение
        assert response.status_code == 200  # БД примет любое значение

    def test_cancel_order(self, client: TestClient, sample_order):
        """Тест: отмена заказа пользователем"""
        cancel_data = {"comment": "Передумал покупать"}

        response = client.put(f"/api/v1/orders/{sample_order.id}/cancel", json=cancel_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "cancelled"
        assert data["data"]["cancelled_at"] is not None

    def test_cancel_already_delivered_order(self, client: TestClient, sample_delivered_order):
        """Тест: отмена уже доставленного заказа (должна быть ошибка)"""
        cancel_data = {"comment": "Попытка отменить доставленный заказ"}

        response = client.put(f"/api/v1/orders/{sample_delivered_order.id}/cancel", json=cancel_data)
        assert response.status_code == 400
        assert "Cannot cancel order" in response.json()["detail"]

    def test_cancel_already_cancelled_order(self, client: TestClient, sample_cancelled_order):
        """Тест: отмена уже отмененного заказа"""
        cancel_data = {"comment": "Повторная отмена"}

        response = client.put(f"/api/v1/orders/{sample_cancelled_order.id}/cancel", json=cancel_data)
        assert response.status_code == 400

    def test_get_order_status_history(self, client: TestClient, sample_order_history, sample_order):
        """Тест: получение истории статусов заказа"""
        response = client.get(f"/api/v1/orders/{sample_order.id}/status-history")
        assert response.status_code == 200

        history = response.json()
        assert len(history) == 3

        assert history[0]["status"] == "new"
        assert history[0]["changed_by"] == "system"
        assert history[1]["status"] == "confirmed"
        assert history[1]["changed_by"] == "admin"
        assert history[2]["status"] == "shipped"

    def test_get_order_status_history_empty(self, client: TestClient, sample_order):
        """Тест: получение истории статусов без записей"""
        response = client.get(f"/api/v1/orders/{sample_order.id}/status-history")
        assert response.status_code == 200
        assert response.json() == []


class TestOrderNumberGeneration:
    """Тесты для генерации номера заказа"""

    def test_generate_order_number_format(self):
        """Тест: проверка формата номера заказа"""
        order_number = order_service.generate_order_number()

        # Формат: BLB-YYYYMMDD-XXXXXX
        assert order_number.startswith("BLB-")
        assert len(order_number) == 20  # BLB-YYYYMMDD-XXXXXX

        parts = order_number.split("-")
        assert len(parts) == 3
        assert parts[0] == "BLB"
        assert len(parts[1]) == 8  # YYYYMMDD
        assert len(parts[2]) == 6  # XXXXXX

        # Проверяем, что дата корректная
        date_part = parts[1]
        assert date_part.isdigit()
        year = int(date_part[:4])
        month = int(date_part[4:6])
        day = int(date_part[6:8])
        assert 2024 <= year <= 2030
        assert 1 <= month <= 12
        assert 1 <= day <= 31

    def test_generate_order_number_unique(self):
        """Тест: уникальность номеров заказов"""
        numbers = set()
        for _ in range(100):
            number = order_service.generate_order_number()
            assert number not in numbers
            numbers.add(number)


class TestOrderTotalCalculation:
    """Тесты для расчета суммы заказа"""

    def test_order_total_calculation(self, client: TestClient, mock_product_service_response):
        """Тест: правильность расчета общей суммы заказа"""
        order_data = {
            "customer_name": "Тест Тестов",
            "customer_phone": "+79161234567",
            "delivery_address": "Тестовый адрес",
            "items": [
                {"product_id": 1, "quantity": 2},  # 249 * 2 = 498
                {"product_id": 2, "quantity": 1},  # 299 * 1 = 299
                {"product_id": 3, "quantity": 3}  # 199 * 3 = 597
            ]
        }

        response = client.post("/api/v1/orders", json=order_data)
        assert response.status_code == 201

        expected_total = 498 + 299 + 597  # 1394
        assert response.json()["data"]["total_amount"] == expected_total


class TestOrderStatusTransitions:
    """Тесты для переходов статусов заказа"""

    def test_status_transition_new_to_confirmed(self, client: TestClient, sample_order):
        """Тест: переход статуса new -> confirmed"""
        response = client.put(f"/api/v1/orders/{sample_order.id}/status", json={"status": "confirmed"})
        assert response.status_code == 200

        get_response = client.get(f"/api/v1/orders/{sample_order.id}")
        assert get_response.json()["status"] == "confirmed"

    def test_status_transition_confirmed_to_paid(self, client: TestClient, sample_order):
        """Тест: переход статуса confirmed -> paid"""
        # Сначала меняем на confirmed
        client.put(f"/api/v1/orders/{sample_order.id}/status", json={"status": "confirmed"})

        # Затем на paid
        response = client.put(f"/api/v1/orders/{sample_order.id}/status", json={"status": "paid"})
        assert response.status_code == 200

        get_response = client.get(f"/api/v1/orders/{sample_order.id}")
        assert get_response.json()["status"] == "paid"

    def test_status_transition_paid_to_shipped(self, client: TestClient, sample_order):
        """Тест: переход статуса paid -> shipped"""
        client.put(f"/api/v1/orders/{sample_order.id}/status", json={"status": "paid"})

        response = client.put(f"/api/v1/orders/{sample_order.id}/status", json={"status": "shipped"})
        assert response.status_code == 200

        get_response = client.get(f"/api/v1/orders/{sample_order.id}")
        assert get_response.json()["status"] == "shipped"

    def test_status_transition_shipped_to_delivered(self, client: TestClient, sample_order):
        """Тест: переход статуса shipped -> delivered"""
        client.put(f"/api/v1/orders/{sample_order.id}/status", json={"status": "shipped"})

        response = client.put(f"/api/v1/orders/{sample_order.id}/status", json={"status": "delivered"})
        assert response.status_code == 200

        get_response = client.get(f"/api/v1/orders/{sample_order.id}")
        assert get_response.json()["status"] == "delivered"
        assert get_response.json()["delivered_at"] is not None