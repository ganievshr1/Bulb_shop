import httpx
from typing import Optional, Dict, Any
from decimal import Decimal
import json

from app.config import settings


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


class ProductService:
    @staticmethod
    async def _make_request(method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to Product Service"""
        url = f"{settings.PRODUCT_SERVICE_URL}{endpoint}"
        
        # Convert Decimal to float in data
        if data:
            data = json.loads(json.dumps(data, cls=DecimalEncoder))
        
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
    async def get_all_products(
            page: int = 1,
            limit: int = 20,
            category_id: Optional[int] = None,
            min_price: Optional[Decimal] = None,
            max_price: Optional[Decimal] = None,
            socket_type: Optional[str] = None,
            is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Get all products with filters"""
        params = {"page": page, "limit": limit}
        if category_id:
            params["category_id"] = category_id
        if min_price:
            params["min_price"] = float(min_price)
        if max_price:
            params["max_price"] = float(max_price)
        if socket_type:
            params["socket_type"] = socket_type
        if is_active is not None:
            params["is_active"] = is_active
        
        url = f"{settings.PRODUCT_SERVICE_URL}/products"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    
    @staticmethod
    async def get_product(product_id: int) -> Dict[str, Any]:
        """Get product by ID"""
        return await ProductService._make_request("GET", f"/products/{product_id}")
    
    @staticmethod
    async def create_product(product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new product"""
        return await ProductService._make_request("POST", "/products", product_data)
    
    @staticmethod
    async def update_product(product_id: int, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update product"""
        return await ProductService._make_request("PUT", f"/products/{product_id}", product_data)
    
    @staticmethod
    async def delete_product(product_id: int) -> None:
        """Delete product (soft delete)"""
        await ProductService._make_request("DELETE", f"/products/{product_id}")
    
    @staticmethod
    async def update_product_stock(product_id: int, stock: int) -> Dict[str, Any]:
        """Update product stock"""
        return await ProductService._make_request("PUT", f"/products/{product_id}/stock", {"stock": stock})
