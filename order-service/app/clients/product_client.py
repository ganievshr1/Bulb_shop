import httpx
from typing import Dict, Any, List
from decimal import Decimal
from app.config import settings


class ProductClient:
    """HTTP клиент для взаимодействия с Product Service"""

    def __init__(self):
        self.base_url = settings.PRODUCT_SERVICE_URL
        self.timeout = 30.0

    async def get_product(self, product_id: int) -> Dict[str, Any]:
        """Получить информацию о товаре"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/products/{product_id}")
            response.raise_for_status()
            return response.json()

    async def get_product_stock(self, product_id: int) -> int:
        """Получить остаток товара"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/products/{product_id}/stock")
            response.raise_for_status()
            data = response.json()
            return data["stock"]

    async def update_product_stock(self, product_id: int, new_stock: int) -> bool:
        """Обновить остаток товара"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.put(
                f"{self.base_url}/products/{product_id}/stock",
                json={"stock": new_stock}
            )
            response.raise_for_status()
            return True

    async def validate_products(self, items: List[Dict]) -> List[Dict]:
        """Проверить наличие и получить информацию о товарах"""
        validated_items = []

        for item in items:
            product = await self.get_product(item["product_id"])
            stock = await self.get_product_stock(item["product_id"])

            if stock < item["quantity"]:
                raise ValueError(
                    f"Insufficient stock for product {product['name']}. "
                    f"Available: {stock}, Required: {item['quantity']}"
                )

            validated_items.append({
                "product_id": item["product_id"],
                "product_name": product["name"],
                "quantity": item["quantity"],
                "unit_price": Decimal(str(product["price"])),
                "total_price": Decimal(str(product["price"])) * item["quantity"]
            })

        return validated_items


# Создаем экземпляр для использования
product_client = ProductClient()