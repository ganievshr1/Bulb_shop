import pytest


class TestAuth:
    def test_login_success(self, client):
        """Test successful login"""
        response = client.post("/api/v1/admin/login", json={
            "login": "test_admin",
            "password": "test123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "token" in data
        assert "admin" in data
        assert data["admin"]["login"] == "test_admin"

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post("/api/v1/admin/login", json={
            "login": "test_admin",
            "password": "wrong_password"
        })
        assert response.status_code == 401

    def test_get_current_admin(self, client, admin_token):
        """Test getting current admin info"""
        response = client.get(
            "/api/v1/admin/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["login"] == "test_admin"

    def test_logout(self, client, admin_token):
        """Test logout"""
        response = client.post(
            "/api/v1/admin/logout",
            json={"token": admin_token},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["success"] is True