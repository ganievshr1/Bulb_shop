#!/bin/bash

echo "=== Заполнение тестовыми данными ==="

# Категории (если нет)
echo "1. Создание категорий..."
curl -X POST http://localhost/api/v1/categories \
  -H "Content-Type: application/json" \
  -d '{"name": "LED лампочки", "description": "Светодиодные лампочки"}' | python3 -m json.tool

# Товары
echo -e "\n2. Создание товаров..."
curl -X POST http://localhost/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "LED E27 7W 2700K",
    "description": "Тёплый белый свет",
    "price": 249.00,
    "category_id": 1,
    "power_watt": 7,
    "socket_type": "E27",
    "color_temp_k": 2700,
    "stock": 100
  }' | python3 -m json.tool

curl -X POST http://localhost/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "LED E27 9W 4000K",
    "description": "Нейтральный белый свет",
    "price": 299.00,
    "category_id": 1,
    "power_watt": 9,
    "socket_type": "E27",
    "color_temp_k": 4000,
    "stock": 85
  }' | python3 -m json.tool

curl -X POST http://localhost/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Smart RGB E27 9W",
    "description": "Умная RGB лампочка",
    "price": 599.00,
    "category_id": 1,
    "power_watt": 9,
    "socket_type": "E27",
    "color_temp_k": 6500,
    "stock": 30
  }' | python3 -m json.tool

echo -e "\n=== Готово! Теперь товары с ID 1, 2, 3 созданы ==="
