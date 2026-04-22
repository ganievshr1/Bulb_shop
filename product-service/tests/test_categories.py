import pytest
from fastapi.testclient import TestClient
from app import models


class TestCategories:
    """Тесты для категорий товаров"""

    def test_get_all_categories_empty(self, client: TestClient, db_session):
        """Тест: получение списка категорий когда их нет"""
        response = client.get("/api/v1/categories")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 0

    def test_get_all_categories(self, client: TestClient, sample_category):
        """Тест: получение списка всех активных категорий"""
        response = client.get("/api/v1/categories")
        assert response.status_code == 200

        categories = response.json()
        assert len(categories) >= 1

        category = categories[0]
        assert "id" in category
        assert "name" in category
        assert "description" in category
        assert "is_active" in category
        assert "created_at" in category
        assert "updated_at" in category
        assert category["name"] == "LED лампочки"
        assert category["is_active"] is True

    def test_get_category_by_id(self, client: TestClient, sample_category):
        """Тест: получение категории по ID"""
        response = client.get(f"/api/v1/categories/{sample_category.id}")
        assert response.status_code == 200

        category = response.json()
        assert category["id"] == sample_category.id
        assert category["name"] == sample_category.name
        assert category["description"] == sample_category.description
        assert category["is_active"] is True

    def test_get_category_not_found(self, client: TestClient):
        """Тест: получение несуществующей категории"""
        response = client.get("/api/v1/categories/99999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Category not found"

    def test_get_inactive_category(self, client: TestClient, db_session):
        """Тест: получение неактивной категории (должна быть скрыта)"""
        # Создаем неактивную категорию
        category = models.Category(
            name="Неактивная категория",
            description="Эта категория должна быть скрыта",
            is_active=False
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        # Пытаемся получить неактивную категорию
        response = client.get(f"/api/v1/categories/{category.id}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Category not found"

    def test_create_category(self, client: TestClient):
        """Тест: создание новой категории"""
        category_data = {
            "name": "Умные лампочки",
            "description": "Лампочки с управлением через Wi-Fi и Bluetooth"
        }

        response = client.post("/api/v1/categories", json=category_data)
        assert response.status_code == 201

        created_category = response.json()
        assert created_category["name"] == category_data["name"]
        assert created_category["description"] == category_data["description"]
        assert created_category["is_active"] is True
        assert "id" in created_category
        assert "created_at" in created_category
        assert "updated_at" in created_category

    def test_create_category_without_description(self, client: TestClient):
        """Тест: создание категории без описания"""
        category_data = {
            "name": "Простая категория"
        }

        response = client.post("/api/v1/categories", json=category_data)
        assert response.status_code == 201

        created_category = response.json()
        assert created_category["name"] == category_data["name"]
        assert created_category["description"] is None

    def test_create_category_duplicate_name(self, client: TestClient, sample_category):
        """Тест: создание категории с дублирующимся именем"""
        category_data = {
            "name": sample_category.name,
            "description": "Дубликат"
        }

        # База данных позволяет дубликаты имен, но API должно корректно обработать
        response = client.post("/api/v1/categories", json=category_data)
        assert response.status_code == 201

        # Проверяем, что создалась новая категория с тем же именем
        created_category = response.json()
        assert created_category["name"] == sample_category.name
        assert created_category["id"] != sample_category.id

    def test_update_category(self, client: TestClient, sample_category):
        """Тест: обновление категории"""
        update_data = {
            "name": "Обновленная LED лампочки",
            "description": "Новое описание категории"
        }

        response = client.put(f"/api/v1/categories/{sample_category.id}", json=update_data)
        assert response.status_code == 200

        updated_category = response.json()
        assert updated_category["name"] == update_data["name"]
        assert updated_category["description"] == update_data["description"]
        assert updated_category["id"] == sample_category.id

    def test_update_category_partial(self, client: TestClient, sample_category):
        """Тест: частичное обновление категории (только имя)"""
        original_description = sample_category.description

        update_data = {
            "name": "Частично обновленная категория"
        }

        response = client.put(f"/api/v1/categories/{sample_category.id}", json=update_data)
        assert response.status_code == 200

        updated_category = response.json()
        assert updated_category["name"] == update_data["name"]
        assert updated_category["description"] == original_description

    def test_update_category_deactivate(self, client: TestClient, sample_category):
        """Тест: деактивация категории через обновление"""
        update_data = {
            "is_active": False
        }

        response = client.put(f"/api/v1/categories/{sample_category.id}", json=update_data)
        assert response.status_code == 200

        updated_category = response.json()
        assert updated_category["is_active"] is False

        # Проверяем, что категория больше не отображается в списке
        list_response = client.get("/api/v1/categories")
        categories = list_response.json()
        assert sample_category.id not in [c["id"] for c in categories]

    def test_update_category_not_found(self, client: TestClient):
        """Тест: обновление несуществующей категории"""
        update_data = {"name": "Несуществующая категория"}

        response = client.put("/api/v1/categories/99999", json=update_data)
        assert response.status_code == 404
        assert response.json()["detail"] == "Category not found"

    def test_delete_category(self, client: TestClient, db_session):
        """Тест: удаление категории (деактивация)"""
        # Создаем категорию для удаления
        category = models.Category(
            name="Категория для удаления",
            description="Будет деактивирована"
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        # Удаляем категорию
        response = client.delete(f"/api/v1/categories/{category.id}")
        assert response.status_code == 204

        # Проверяем, что категория деактивирована (не возвращается в списке)
        get_response = client.get(f"/api/v1/categories/{category.id}")
        assert get_response.status_code == 404

        # Проверяем, что категория все еще существует в БД, но неактивна
        db_session.refresh(category)
        assert category.is_active is False

    def test_delete_category_not_found(self, client: TestClient):
        """Тест: удаление несуществующей категории"""
        response = client.delete("/api/v1/categories/99999")
        assert response.status_code == 404

    def test_categories_with_products(self, client: TestClient, sample_category, sample_product):
        """Тест: получение категории, у которой есть товары"""
        response = client.get(f"/api/v1/categories/{sample_category.id}")
        assert response.status_code == 200

        category = response.json()
        assert category["name"] == sample_category.name

        # Проверяем, что товары связаны с категорией
        products_response = client.get(f"/api/v1/products/category/{sample_category.id}")
        assert products_response.status_code == 200
        products_data = products_response.json()
        assert products_data["success"] is True
        assert len(products_data["data"]) >= 1

    def test_create_category_with_long_name(self, client: TestClient):
        """Тест: создание категории с очень длинным названием"""
        long_name = "A" * 200  # 200 символов, но ограничение в БД 100

        category_data = {
            "name": long_name,
            "description": "Очень длинное название"
        }

        response = client.post("/api/v1/categories", json=category_data)
        # Должна быть ошибка валидации
        assert response.status_code == 422  # Validation error

    def test_get_categories_pagination_implicit(self, client: TestClient, db_session):
        """Тест: пагинация категорий (неявная, т.к. все категории возвращаются)"""
        # Создаем несколько категорий
        for i in range(5):
            category = models.Category(
                name=f"Категория {i}",
                description=f"Описание {i}"
            )
            db_session.add(category)
        db_session.commit()

        response = client.get("/api/v1/categories")
        assert response.status_code == 200

        categories = response.json()
        # Должны быть все активные категории
        active_categories = db_session.query(models.Category).filter(
            models.Category.is_active == True
        ).count()
        assert len(categories) == active_categories

    def test_category_response_format(self, client: TestClient, sample_category):
        """Тест: проверка формата ответа категории"""
        response = client.get(f"/api/v1/categories/{sample_category.id}")
        assert response.status_code == 200

        category = response.json()

        # Проверяем типы полей
        assert isinstance(category["id"], int)
        assert isinstance(category["name"], str)
        assert isinstance(category["is_active"], bool)
        assert isinstance(category["created_at"], str)
        assert isinstance(category["updated_at"], str)

        # description может быть None или str
        assert category["description"] is None or isinstance(category["description"], str)

    def test_multiple_categories_response(self, client: TestClient, db_session):
        """Тест: получение нескольких категорий"""
        # Создаем несколько категорий
        categories_data = [
            {"name": "Категория A", "description": "Описание A"},
            {"name": "Категория B", "description": "Описание B"},
            {"name": "Категория C", "description": "Описание C"}
        ]

        for cat_data in categories_data:
            category = models.Category(**cat_data)
            db_session.add(category)
        db_session.commit()

        response = client.get("/api/v1/categories")
        assert response.status_code == 200

        categories = response.json()
        assert len(categories) >= 3

        # Проверяем, что все созданные категории есть в ответе
        category_names = [c["name"] for c in categories]
        for cat_data in categories_data:
            assert cat_data["name"] in category_names


class TestCategoriesIntegration:
    """Интеграционные тесты категорий с товарами"""

    def test_category_with_products_cascade(self, client: TestClient, db_session):
        """Тест: удаление категории не удаляет товары, только деактивирует категорию"""
        # Создаем категорию
        category = models.Category(name="Тестовая категория")
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        # Создаем товар в этой категории
        product = models.Product(
            name="Тестовый товар",
            price=100.00,
            category_id=category.id,
            stock=10,
            is_active=True
        )
        db_session.add(product)
        db_session.commit()

        # Удаляем категорию (деактивируем)
        response = client.delete(f"/api/v1/categories/{category.id}")
        assert response.status_code == 204

        # Проверяем, что товар все еще существует и активен
        product_response = client.get(f"/api/v1/products/{product.id}")
        assert product_response.status_code == 200
        assert product_response.json()["is_active"] is True

        # Проверяем, что категория неактивна
        category_response = client.get(f"/api/v1/categories/{category.id}")
        assert category_response.status_code == 404

    def test_get_products_by_inactive_category(self, client: TestClient, db_session):
        """Тест: получение товаров по неактивной категории"""
        # Создаем неактивную категорию
        category = models.Category(
            name="Неактивная категория",
            is_active=False
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        # Создаем товар в неактивной категории
        product = models.Product(
            name="Товар в неактивной категории",
            price=100.00,
            category_id=category.id,
            stock=10,
            is_active=True
        )
        db_session.add(product)
        db_session.commit()

        # Пытаемся получить товары по неактивной категории
        response = client.get(f"/api/v1/products/category/{category.id}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Category not found"