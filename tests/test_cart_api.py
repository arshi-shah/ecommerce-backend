import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Sample user credentials to generate token
test_user = {
    "email": "user01@gmail.com",
    "password": "userpass"
}

# Use a valid product ID created by admin
VALID_PRODUCT_ID = 5  # Replace with real ID in your DB
INVALID_PRODUCT_ID = 9999

def get_user_token():
    response = client.post("/auth/signin", json=test_user)
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture(scope="module")
def user_token():
    return get_user_token()

@pytest.fixture(scope="module")
def auth_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}

def test_add_to_cart_success(auth_headers):
    response = client.post("/cart/", json={
        "product_id": VALID_PRODUCT_ID,
        "quantity": 1
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["product_id"] == VALID_PRODUCT_ID

def test_add_to_cart_product_not_found(auth_headers):
    response = client.post("/cart/", json={
        "product_id": INVALID_PRODUCT_ID,
        "quantity": 1
    }, headers=auth_headers)
    assert response.status_code == 404

def test_add_to_cart_insufficient_stock(auth_headers):
    response = client.post("/cart/", json={
        "product_id": VALID_PRODUCT_ID,
        "quantity": 9999
    }, headers=auth_headers)
    assert response.status_code == 400

def test_view_cart(auth_headers):
    response = client.get("/cart/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_cart_to_zero(auth_headers):
    response = client.put(f"/cart/{VALID_PRODUCT_ID}", json={
        "quantity": 0
    }, headers=auth_headers)
    assert response.status_code == 204


def test_update_cart_to_zero(auth_headers):
    response = client.put(f"/cart/{VALID_PRODUCT_ID}", json={
        "quantity": 0
    }, headers=auth_headers)
    assert response.status_code == 200

def test_remove_from_cart_not_found(auth_headers):
    response = client.delete(f"/cart/{INVALID_PRODUCT_ID}", headers=auth_headers)
    assert response.status_code == 404

def test_add_and_remove_product(auth_headers):
    # Add first
    response = client.post("/cart/", json={
        "product_id": VALID_PRODUCT_ID,
        "quantity": 1
    }, headers=auth_headers)
    assert response.status_code == 200

    # Then remove
    response = client.delete(f"/cart/{VALID_PRODUCT_ID}", headers=auth_headers)
    assert response.status_code == 200
