import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

test_admin = {
    "email": "admin01@gmail.com",
    "password": "adminpass"
}

test_product = {
    "name": "Test Product",
    "description": "Sample product",
    "price": 99.99,
    "stock": 50,
    "category": "Electronics",  # required
    "image_url": "http://example.com/image.jpg"  # optional
}


@pytest.fixture(scope="module")
def admin_token():
    response = client.post("/auth/signin", json=test_admin)
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture(scope="module")
def created_product_id(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.post("/admin/products/", json=test_product, headers=headers)
    assert response.status_code in [200, 201]
    return response.json()["id"]

def test_get_all_products(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/admin/products/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_product_by_id(admin_token, created_product_id):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get(f"/admin/products/{created_product_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == created_product_id

def test_update_product(admin_token, created_product_id):
    headers = {"Authorization": f"Bearer {admin_token}"}
    updated_data = {
        "name": "Updated Product",
        "description": "Updated description",
        "price": 49.99,
        "stock": 20,
        "category": "Updated Category",  # ✅ required
        "image_url": "http://example.com/updated.jpg"  # optional
    }
    response = client.put(f"/admin/products/{created_product_id}", json=updated_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == updated_data["name"]


# def test_delete_product(admin_token, created_product_id):
#     headers = {"Authorization": f"Bearer {admin_token}"}
#     response = client.delete(f"/admin/products/{created_product_id}", headers=headers)
#     assert response.status_code == 204
