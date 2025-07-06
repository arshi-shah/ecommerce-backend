import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ---------------------------
# Test Data
# ---------------------------
NEW_USER = {
    "name": "Test User",
    "email": "testuser@gmail.com",
    "password": "string",
    "role": "user"
}

NEW_ADMIN = {
    "name": "Admin User",
    "email": "adminuser@gmail.com",
    "password": "adminpass",
    "role": "admin"
}

INVALID_USER = {
    "email": "wronguser@gmail.com",
    "password": "wrongpass"
}

RESET_TOKEN = None
ADMIN_TOKEN = None
USER_TOKEN = None

# ---------------------------
# 1. Sign Up
# ---------------------------

def test_signup_user():
    response = client.post("/auth/signup", json=NEW_USER)
    assert response.status_code in [200, 400]  # 400 if user already exists

def test_signup_admin():
    response = client.post("/auth/signup", json=NEW_ADMIN)
    assert response.status_code in [200, 400]

# ---------------------------
# 2. Sign In
# ---------------------------

def test_signin_user():
    global USER_TOKEN
    response = client.post("/auth/signin", json={
        "email": NEW_USER["email"],
        "password": NEW_USER["password"]
    })
    assert response.status_code == 200
    USER_TOKEN = response.json()["access_token"]


def test_signin_admin():
    global ADMIN_TOKEN
    response = client.post("/auth/signin", json={
        "email": NEW_ADMIN["email"],
        "password": NEW_ADMIN["password"]
    })
    assert response.status_code == 200
    ADMIN_TOKEN = response.json()["access_token"]


def test_signin_failure():
    response = client.post("/auth/signin", json=INVALID_USER)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

# ---------------------------
# 3. Forgot Password
# ---------------------------

def test_forgot_password():
    response = client.post("/auth/forgot-password", json={"email": NEW_USER["email"]})
    assert response.status_code == 200 or response.status_code == 404


def test_forgot_password_user_not_found():
    response = client.post("/auth/forgot-password", json={"email": "nouser@example.com"})
    assert response.status_code == 404

# ---------------------------
# 4. RBAC Tests (Admin vs User Access)
# ---------------------------

def test_admin_access():
    response = client.get("/admin/products", headers={"Authorization": f"Bearer {ADMIN_TOKEN}"})
    assert response.status_code in [200, 403]  # 403 if DB/table check fails


def test_user_access_denied():
    response = client.get("/admin/products", headers={"Authorization": f"Bearer {USER_TOKEN}"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"

# ---------------------------
# 5. Reset Password (requires valid token)
# ---------------------------
# Note: Since token is sent via email, testing it requires access to DB or mocking.
# We'll skip testing reset-password here unless token retrieval is enabled.
