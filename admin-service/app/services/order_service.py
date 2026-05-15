import httpx
from typing import Optional, Dict, Any

from app.config import settings


class OrderService:
    @staticmethod
    async def _make_request(method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to Order Service"""
        url = f"{settings.ORDER_SERVICE_URL}{endpoint}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "GET":
                response = await client.get(url)
            elif method == "POST":
                response = await client.post(url, json=data)
            elif method == "PUT":
                response = await client.put(url, json=data)
            elif method == "DELETE":
                response = await client.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

    @staticmethod
    async def get_all_orders(
            page: int = 1,
            limit: int = 20,
            status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get all orders with filters"""
        url = f"{settings.ORDER_SERVICE_URL}/orders"
        params = {"page": page, "limit": limit}
        if status:
            params["status"] = status

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def get_order(order_id: int) -> Dict[str, Any]:
        """Get order by ID"""
        return await OrderService._make_request("GET", f"/orders/{order_id}")

    @staticmethod
    async def update_order_status(order_id: int, status: str) -> Dict[str, Any]:
        """Update order status"""
        return await OrderService._make_request("PUT", f"/orders/{order_id}/status", {"status": status})