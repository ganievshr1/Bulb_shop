import pytest
from unittest.mock import patch


class TestAdminProducts:
    @patch('app.services.product_service.ProductService.get_all_products')
    def test_get_products(self, mock_get_all, client, admin_token):
        """Test getting all products"""
        mock_get_all.return_value = {
            "success": True,
            "data": [{"id": 1, "name": "Test Product"}],
            "pagination": {"page": 1, "limit": 20, "total": 1}
        }

        response = client.get(
            "/api/v1/admin/products",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

    def test_get_products_unauthorized(self, client):
        """Test getting products without token"""
        response = client.get("/api/v1/admin/products")
        assert response.status_code == 401