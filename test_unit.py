import pytest
from fastapi.testclient import TestClient
from main import app 

client = TestClient(app)

# Fixture untuk membuat customer yang akan digunakan oleh tes
@pytest.fixture
def create_test_customer():
    customer_data = {"name": "Test Customer", "email": "test@example.com", "phone": "123456"}
    response = client.post("/customers", json=customer_data)
    return response.json()

# Tes untuk membuat customer
def test_create_customer(create_test_customer):
    assert "message" in create_test_customer
    assert create_test_customer["message"] == "Customer created successfully"

# Tes untuk mendapatkan customer yang dibuat
def test_get_customer(create_test_customer):
    customer_id = create_test_customer["customer"]["id"]  # Pastikan 'customer' ada
    response = client.get(f"/customers/{customer_id}")
    assert response.status_code == 200
    assert response.json()["id"] == customer_id