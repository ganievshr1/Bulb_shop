#!/usr/bin/env python3
"""
Скрипт для заполнения Product Service тестовыми данными
"""

import asyncio
import httpx
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:8081/api/v1"

# Категории
CATEGORIES = [
    {"name": "LED лампочки", "description": "Светодиодные лампочки с низким энергопотреблением"},
    {"name": "Энергосберегающие", "description": "Компактные люминесцентные лампы"},
    {"name": "Декоративные", "description": "Лампочки для декоративного освещения"},
    {"name": "Умные лампочки", "description": "С управлением через Wi-Fi и Bluetooth"},
]

# Товары
PRODUCTS = [
    {
        "name": "LED E27 7W 2700K",
        "description": "Тёплый белый свет, 806 люмен",
        "price": 249.00,
        "category_id": 1,
        "power_watt": 7,
        "socket_type": "E27",
        "color_temp_k": 2700,
        "lumen": 806,
        "lifespan_hours": 25000,
        "stock": 100
    },
    {
        "name": "LED E27 9W 4000K",
        "description": "Нейтральный белый свет",
        "price": 299.00,
        "category_id": 1,
        "power_watt": 9,
        "socket_type": "E27",
        "color_temp_k": 4000,
        "lumen": 1055,
        "lifespan_hours": 25000,
        "stock": 85
    },
    {
        "name": "LED GU10 5W 6500K",
        "description": "Холодный белый свет",
        "price": 199.00,
        "category_id": 1,
        "power_watt": 5,
        "socket_type": "GU10",
        "color_temp_k": 6500,
        "lumen": 450,
        "lifespan_hours": 20000,
        "stock": 120
    },
    {
        "name": "Smart RGB E27 9W",
        "description": "Умная RGB лампочка",
        "price": 599.00,
        "category_id": 4,
        "power_watt": 9,
        "socket_type": "E27",
        "color_temp_k": 6500,
        "lumen": 800,
        "lifespan_hours": 25000,
        "stock": 30
    },
]


async def seed_categories():
    """Заполнение категорий"""
    async with httpx.AsyncClient() as client:
        for category in CATEGORIES:
            try:
                response = await client.post(f"{BASE_URL}/categories", json=category)
                if response.status_code == 201:
                    print(f"✓ Создана категория: {category['name']}")
                else:
                    print(f"✗ Ошибка при создании категории {category['name']}: {response.status_code}")
            except Exception as e:
                print(f"✗ Ошибка: {e}")


async def seed_products():
    """Заполнение товаров"""
    async with httpx.AsyncClient() as client:
        for product in PRODUCTS:
            try:
                response = await client.post(f"{BASE_URL}/products", json=product)
                if response.status_code == 201:
                    print(f"✓ Создан товар: {product['name']}")
                else:
                    print(f"✗ Ошибка при создании товара {product['name']}: {response.status_code}")
            except Exception as e:
                print(f"✗ Ошибка: {e}")


async def main():
    print("Начало заполнения базы данных Product Service...")
    await seed_categories()
    await seed_products()
    print("Заполнение завершено!")


if __name__ == "__main__":
    asyncio.run(main())