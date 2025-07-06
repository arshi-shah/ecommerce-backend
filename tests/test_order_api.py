import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Sample user credentials to generate token
test_user = {
    "email": "user01@gmail.com",
    "password": "userpass"
}

@pytest.fixture(scope="module")
def user_token():
    response = client.post("/auth/signin", json=test_user)
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture(scope="module")
def auth_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}

def test_create_order(auth_headers):
    response = client.post("/orders/", headers=auth_headers)
    assert response.status_code in [200, 201]
    assert "id" in response.json()

def test_get_user_orders(auth_headers):
    response = client.get("/orders/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_order_by_id(auth_headers):
    # First, create an order
    response = client.post("/orders/", headers=auth_headers)
    assert response.status_code in [200, 201]
    order_id = response.json()["id"]

    # Then, fetch it by ID
    response = client.get(f"/orders/1", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == order_id

def test_get_order_not_found(auth_headers):
    response = client.get("/orders/99999", headers=auth_headers)
    assert response.status_code == 404
