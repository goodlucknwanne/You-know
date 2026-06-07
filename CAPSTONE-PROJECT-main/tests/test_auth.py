import pytest
from tests.conftest import auth_headers, register_and_login


class TestRegister:
    def test_register_student_success(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={"name": "Alice", "email": "alice@test.com", "password": "secret123", "role": "student"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "alice@test.com"
        assert data["role"] == "student"
        assert data["is_active"] is True
        assert "hashed_password" not in data

    def test_register_admin_success(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={"name": "Bob Admin", "email": "admin@test.com", "password": "admin1234", "role": "admin"},
        )
        assert resp.status_code == 201
        assert resp.json()["role"] == "admin"

    def test_register_duplicate_email(self, client):
        payload = {"name": "Alice", "email": "alice@test.com", "password": "secret123"}
        client.post("/api/v1/auth/register", json=payload)
        resp = client.post("/api/v1/auth/register", json=payload)
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"].lower()

    def test_register_invalid_email(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={"name": "Alice", "email": "not-an-email", "password": "secret123"},
        )
        assert resp.status_code == 422

    def test_register_short_password(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={"name": "Alice", "email": "alice@test.com", "password": "123"},
        )
        assert resp.status_code == 422

    def test_register_invalid_role(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={"name": "Alice", "email": "alice@test.com", "password": "secret123", "role": "superuser"},
        )
        assert resp.status_code == 422

    def test_register_empty_name(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={"name": "   ", "email": "alice@test.com", "password": "secret123"},
        )
        assert resp.status_code == 422

    def test_register_default_role_is_student(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={"name": "Alice", "email": "alice@test.com", "password": "secret123"},
        )
        assert resp.status_code == 201
        assert resp.json()["role"] == "student"


class TestLogin:
    def test_login_success(self, client):
        client.post(
            "/api/v1/auth/register",
            json={"name": "Alice", "email": "alice@test.com", "password": "secret123"},
        )
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "alice@test.com", "password": "secret123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        client.post(
            "/api/v1/auth/register",
            json={"name": "Alice", "email": "alice@test.com", "password": "secret123"},
        )
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "alice@test.com", "password": "wrongpassword"},
        )
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@test.com", "password": "password123"},
        )
        assert resp.status_code == 401

    def test_login_inactive_user(self, client, db):
        from app.models.user import User
        client.post(
            "/api/v1/auth/register",
            json={"name": "Alice", "email": "alice@test.com", "password": "secret123"},
        )
        user = db.query(User).filter(User.email == "alice@test.com").first()
        user.is_active = False
        db.commit()

        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "alice@test.com", "password": "secret123"},
        )
        assert resp.status_code == 403


class TestGetProfile:
    def test_get_profile_authenticated(self, client):
        token = register_and_login(client, "alice@test.com", "secret123")
        resp = client.get("/api/v1/auth/me", headers=auth_headers(token))
        assert resp.status_code == 200
        assert resp.json()["email"] == "alice@test.com"

    def test_get_profile_unauthenticated(self, client):
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    def test_get_profile_invalid_token(self, client):
        resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalidtoken"})
        assert resp.status_code == 401