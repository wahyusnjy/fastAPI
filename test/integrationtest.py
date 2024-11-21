import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from fastapi.testclient import TestClient
from app.postgresql.mainpostgre import app
from urllib.parse import urlencode

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Customer API"}

def test_get_all_customers_empty():
    response = client.get("/customers")
    assert response.status_code == 200
    assert response.json() == [
        {"phone": "9876543210", "name": "Jane Doe", "id": 1, "email": "jane.doe@example.com"}
    ]

def test_create_customer():
    payload = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "1234567890"
    }
    query_string = urlencode(payload)
    response = client.post(f"/customers?{query_string}")
    assert response.status_code == 200
    assert response.json()["message"] == "Customer created successfully"
    assert response.json()["customer"]["name"] == "John Doe"

def test_get_customer():
    response = client.get("/customers/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Jane Doe"

def test_update_customer():
    updated_payload = {
        "name": "John Updated",
        "email": "john.updated@example.com",
        "phone": "5559876543"
    }
    query_string_update = urlencode(updated_payload)
    response = client.put(f"/customers/2?{query_string_update}")
    assert response.status_code == 200
    assert response.json()["customer"]["name"] == "John Updated"

def test_delete_customer():
    response = client.delete("/customers/2")
    assert response.status_code == 200
    assert response.json()["message"] == "Customer deleted successfully"
