import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from fastapi.testclient import TestClient
from app.sqlite.main import app
from urllib.parse import urlencode

client = TestClient(app)
customer_id = None
username = 'John Doe'

# Define a constant for the error message
CUSTOMER_ID_NOT_NONE_MSG = "Customer ID should not be None"

def test_read_root():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Customer API"}

def test_create_customer():
    """Test customer creation."""
    global customer_id
    payload = {
        "name": username,
        "email": "john.doe@example.com",
        "phone": "1234567890"
    }
    query_string = urlencode(payload)
    response = client.post(f"/customers?{query_string}")
    assert response.status_code == 200
    assert response.json()["message"] == "Customer created successfully"
    assert response.json()["customer"]["name"] == username
    customer_id = response.json()["customer"]["id"]

def test_get_customer():
    """Test retrieving a specific customer."""
    global customer_id
    assert customer_id is not None, CUSTOMER_ID_NOT_NONE_MSG
    response = client.get(f"/customers/{customer_id}")
    assert response.status_code == 200
    assert response.json()["name"] == username

def test_update_customer():
    """Test updating customer information."""
    global customer_id
    assert customer_id is not None, CUSTOMER_ID_NOT_NONE_MSG
    updated_payload = {
        "name": username,
        "email": "john.dobleh@example.com",
        "phone": "5559876543"
    }
    query_string_update = urlencode(updated_payload)
    response = client.put(f"/customers/{customer_id}?{query_string_update}")
    assert response.status_code == 200
    assert response.json()["customer"]["name"] == username
    assert response.json()["customer"]["email"] == "john.dobleh@example.com"

def test_delete_customer():
    """Test deleting a customer."""
    global customer_id
    assert customer_id is not None, CUSTOMER_ID_NOT_NONE_MSG
    response = client.delete(f"/customers/{customer_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Customer deleted successfully"

def test_get_customer_after_deletion():
    """Test retrieving a customer after deletion (should fail)."""
    global customer_id
    assert customer_id is not None, CUSTOMER_ID_NOT_NONE_MSG
    response = client.get(f"/customers/{customer_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"
