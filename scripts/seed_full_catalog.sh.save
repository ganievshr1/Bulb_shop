#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:8081/api/v1"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Заполнение каталога лампочек${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Проверка доступности API
echo -e "${YELLOW}Проверка доступности API...${NC}"
if curl -s http://localhost:8081/health > /dev/null; then
    echo -e "${GREEN}✅ API доступен${NC}\n"
else
    echo -e "${RED}❌ API не доступен! Запусти бэкэнд: make up${NC}"
    exit 1
fi

# === 1. СОЗДАНИЕ КАТЕГОРИЙ ===
echo -e "${YELLOW}📁 Создание категорий...${NC}"

# Категория 1: LED лампочки
echo "Создание категории: LED лампочки"
curl -s -X POST "$BASE_URL/categories" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "LED лампочки",
    "description": "Светодиодные лампочки с низким энергопотреблением и долгим сроком службы"
  }' | python3 -m json.tool

# Категория 2: Энергосберегающие
echo -e "\nСоздание категории: Энергосберегающие"
curl -s -X POST "$BASE_URL/categories" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Энергосберегающие",
    "description": "Компактные люминесцентные лампы для экономии электроэнергии"
  }' | python3 -m json.tool

# Категория 3: Декоративные
echo -e "\nСоздание категории: Декоративные"
curl -s -X POST "$BASE_URL/categories" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Декоративные",
    "description": "Лампочки для декоративного освещения и создания уюта"
  }' | python3 -m json.tool

# Категория 4: Умные лампочки
echo -e "\nСоздание категории: Умные лампочки"
curl -s -X POST "$BASE_URL/categories" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Умные лампочки",
    "description": "С управлением через Wi-Fi, Bluetooth и голосовых помощников"
  }' | python3 -m json.tool

# Категория 5: Галогенные
echo -e "\nСоздание категории: Галогенные"
curl -s -X POST "$BASE_URL/categories" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Галогенные",
    "description": "Яркий и насыщенный свет, компактные размеры"
  }' | python3 -m json.tool

echo -e "\n${GREEN}✅ Категории созданы!${NC}\n"
sleep 2

# === 2. ТОВАРЫ ДЛЯ КАТЕГОРИИ "LED лампочки" (category_id=1) ===
echo -e "${YELLOW}💡 Создание товаров для категории LED лампочки...${NC}"

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "LED E27 7W 2700K",
    "description": "Тёплый белый свет, 806 люмен, угол рассеивания 120°",
    "price": 249,
    "category_id": 1,
    "power_watt": 7,
    "socket_type": "E27",
    "color_temp_k": 2700,
    "lumen": 806,
    "lifespan_hours": 25000,
    "stock": 100
  }'

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "LED E27 9W 4000K",
    "description": "Нейтральный белый свет, 1055 люмен, идеально для офиса",
    "price": 299,
    "category_id": 1,
    "power_watt": 9,
    "socket_type": "E27",
    "color_temp_k": 4000,
    "lumen": 1055,
    "lifespan_hours": 25000,
    "stock": 85
  }'

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "LED GU10 5W 6500K",
    "description": "Холодный белый свет, 450 люмен, поворотный спот",
    "price": 199,
    "category_id": 1,
    "power_watt": 5,
    "socket_type": "GU10",
    "color_temp_k": 6500,
    "lumen": 450,
    "lifespan_hours": 20000,
    "stock": 120
  }'

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "LED E14 6W 3000K",
    "description": "Тёплый свет, форма свечи, 470 люмен",
    "price": 179,
    "category_id": 1,
    "power_watt": 6,
    "socket_type": "E14",
    "color_temp_k": 3000,
    "lumen": 470,
    "lifespan_hours": 20000,
    "stock": 150
  }'

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "LED GX53 12W 4000K",
    "description": "Плоская круглая лампа, 1300 люмен, для подвесных потолков",
    "price": 399,
    "category_id": 1,
    "power_watt": 12,
    "socket_type": "GX53",
    "color_temp_k": 4000,
    "lumen": 1300,
    "lifespan_hours": 30000,
    "stock": 60
  }'

echo -e "\n${GREEN}✅ Товары для LED лампочек добавлены!${NC}\n"
sleep 1

# === 3. ТОВАРЫ ДЛЯ КАТЕГОРИИ "Энергосберегающие" (category_id=2) ===
echo -e "${YELLOW}💡 Создание товаров для категории Энергосберегающие...${NC}"

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Энергосберегающая E27 15W",
    "description": "Компактная люминесцентная лампа, 900 люмен, тёплый свет",
    "price": 129,
    "category_id": 2,
    "power_watt": 15,
    "socket_type": "E27",
    "color_temp_k": 2700,
    "lumen": 900,
    "lifespan_hours": 8000,
    "stock": 50
  }'

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Энергосберегающая E27 20W",
    "description": "Яркая лампа 1200 люмен, нейтральный свет",
    "price": 159,
    "category_id": 2,
    "power_watt": 20,
    "socket_type": "E27",
    "color_temp_k": 4000,
    "lumen": 1200,
    "lifespan_hours": 8000,
    "stock": 45
  }'

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Энергосберегающая E14 11W",
    "description": "Свеча, 600 люмен, тёплый свет для люстр",
    "price": 99,
    "category_id": 2,
    "power_watt": 11,
    "socket_type": "E14",
    "color_temp_k": 2700,
    "lumen": 600,
    "lifespan_hours": 6000,
    "stock": 80
  }'

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Энергосберегающая GU10 11W",
    "description": "Спот для точечного освещения, 550 люмен",
    "price": 119,
    "category_id": 2,
    "power_watt": 11,
    "socket_type": "GU10",
    "color_temp_k": 3000,
    "lumen": 550,
    "lifespan_hours": 7000,
    "stock": 70
  }'

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Энергосберегающая GX53 15W",
    "description": "Круглая лампа 850 люмен для офисов",
    "price": 149,
    "category_id": 2,
    "power_watt": 15,
    "socket_type": "GX53",
    "color_temp_k": 4000,
    "lumen": 850,
    "lifespan_hours": 8000,
    "stock": 55
  }'

echo -e "\n${GREEN}✅ Товары для энергосберегающих добавлены!${NC}\n"
sleep 1

# === 4. ТОВАРЫ ДЛЯ КАТЕГОРИИ "Декоративные" (category_id=3) ===
echo -e "${YELLOW}💡 Создание товаров для категории Декоративные...${NC}"

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Декор E14 4W Свеча на ветру",
    "description": "Декоративная свеча с эффектом мерцания, тёплый свет",
    "price": 89,
    "category_id": 3,
    "power_watt": 4,
    "socket_type": "E14",
    "color_temp_k": 2200,
    "lumen": 250,
    "lifespan_hours": 15000,
    "stock": 200
  }'

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Декор E27 6W Шар матовый",
    "description": "Стеклянный шар, мягкий рассеянный свет",
    "price": 149,
    "category_id": 3,
    "power_watt": 6,
    "socket_type": "E27",
    "color_temp_k": 2700,
    "lumen": 400,
    "lifespan_hours": 20000,
    "stock": 120
  }'

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Декор G9 3W Капля",
    "description": "Миниатюрная лампа-капля для бра и люстр",
    "price": 69,
    "category_id": 3,
    "power_watt": 3,
    "socket_type": "G9",
    "color_temp_k": 3000,
    "lumen": 200,
    "lifespan_hours": 15000,
    "stock": 300
  }'

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Декор E27 8W Ретро-нить",
    "description": "Лампа в стиле ретро с видимой нитью накала",
    "price": 199,
    "category_id": 3,
    "power_watt": 8,
    "socket_type": "E27",
    "color_temp_k": 2400,
    "lumen": 350,
    "lifespan_hours": 10000,
    "stock": 80
  }'

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Декор E14 5W Свеча матовая",
    "description": "Матовая свеча для люстр, мягкий свет",
    "price": 109,
    "category_id": 3,
    "power_watt": 5,
    "socket_type": "E14",
    "color_temp_k": 2700,
    "lumen": 350,
    "lifespan_hours": 18000,
    "stock": 150
  }'

echo -e "\n${GREEN}✅ Товары для декоративных добавлены!${NC}\n"
sleep 1

# === 5. ТОВАРЫ ДЛЯ КАТЕГОРИИ "Умные лампочки" (category_id=4) ===
echo -e "${YELLOW}💡 Создание товаров для категории Умные лампочки...${NC}"

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Smart RGB E27 9W",
    "description": "Умная RGB лампочка, 16 млн цветов, управление с телефона",
    "price": 599,
    "category_id": 4,
    "power_watt": 9,
    "socket_type": "E27",
    "color_temp_k": 6500,
    "lumen": 800,
    "lifespan_hours": 25000,
    "stock": 30
  }'

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Smart White E27 8W",
    "description": "Умная лампочка с регулировкой яркости и температуры",
    "price": 399,
    "category_id": 4,
    "power_watt": 8,
    "socket_type": "E27",
    "color_temp_k": 4000,
    "lumen": 700,
    "lifespan_hours": 25000,
    "stock": 45
  }'

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Smart RGB GU10 7W",
    "description": "Умный спот для точечного освещения, RGB",
    "price": 499,
    "category_id": 4,
    "power_watt": 7,
    "socket_type": "GU10",
    "color_temp_k": 6500,
    "lumen": 550,
    "lifespan_hours": 20000,
    "stock": 25
  }'

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Smart Strip LED",
    "description": "Умная LED-лента 2м, адресная подсветка",
    "price": 1299,
    "category_id": 4,
    "power_watt": 24,
    "socket_type": "LED Strip",
    "color_temp_k": 6500,
    "lumen": 1600,
    "lifespan_hours": 30000,
    "stock": 20
  }'

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Smart Filament E27 6W",
    "description": "Умная ретро-лампа с эффектом нити",
    "price": 699,
    "category_id": 4,
    "power_watt": 6,
    "socket_type": "E27",
    "color_temp_k": 2700,
    "lumen": 470,
    "lifespan_hours": 20000,
    "stock": 35
  }'

echo -e "\n${GREEN}✅ Товары для умных лампочек добавлены!${NC}\n"
sleep 1

# === 6. ТОВАРЫ ДЛЯ КАТЕГОРИИ "Галогенные" (category_id=5) ===
echo -e "${YELLOW}💡 Создание товаров для категории Галогенные...${NC}"

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Галогенная E27 42W",
    "description": "Яркий свет 750 люмен, идеально для гостиной",
    "price": 89,
    "category_id": 5,
    "power_watt": 42,
    "socket_type": "E27",
    "color_temp_k": 2800,
    "lumen": 750,
    "lifespan_hours": 2000,
    "stock": 60
  }'

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Галогенная GU10 35W",
    "description": "Спот для точечного освещения, 600 люмен",
    "price": 79,
    "category_id": 5,
    "power_watt": 35,
    "socket_type": "GU10",
    "color_temp_k": 3000,
    "lumen": 600,
    "lifespan_hours": 2000,
    "stock": 70
  }'

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Галогенная G9 28W",
    "description": "Компактная лампа 400 люмен для бра",
    "price": 69,
    "category_id": 5,
    "power_watt": 28,
    "socket_type": "G9",
    "color_temp_k": 2800,
    "lumen": 400,
    "lifespan_hours": 2000,
    "stock": 90
  }'

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Галогенная E14 28W",
    "description": "Лампа-свеча 400 люмен для люстр",
    "price": 79,
    "category_id": 5,
    "power_watt": 28,
    "socket_type": "E14",
    "color_temp_k": 2700,
    "lumen": 400,
    "lifespan_hours": 2000,
    "stock": 85
  }'

curl -s -X POST "$BASE_URL/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Галогенная R7s 118mm",
    "description": "Линейная галогенная лампа для прожекторов",
    "price": 149,
    "category_id": 5,
    "power_watt": 150,
    "socket_type": "R7s",
    "color_temp_k": 2900,
    "lumen": 2400,
    "lifespan_hours": 2000,
    "stock": 40
  }'

echo -e "\n${GREEN}✅ Товары для галогенных добавлены!${NC}\n"
sleep 1

# === ИТОГИ ===
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}📊 ИТОГИ ЗАПОЛНЕНИЯ:${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "✅ Создано категорий: 5"
echo -e "✅ Создано товаров: 25 (5 в каждой категории)"
echo -e "✅ Всего товаров в каталоге: 25+"
echo -e "${GREEN}========================================${NC}"
echo -e "\n🎉 Заполнение каталога завершено успешно!"
echo -e "🌐 Открой фронтэнд: http://localhost:3000/catalog"
