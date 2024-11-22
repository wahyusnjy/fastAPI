import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from fastapi.testclient import TestClient
from app.sqlite.main import app
from urllib.parse import urlencode

client = TestClient(app)
customer_id = None
username = 'John Doe'

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Customer API"}

def test_create_customer():
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
    global customer_id
    response = client.get(f"/customers/{customer_id}")
    assert response.status_code == 200
    assert response.json()["name"] == username

def test_update_customer():
    global customer_id
    updated_payload = {
        "name": username,
        "email": "john.dobleh@example.com",
        "phone": "5559876543"
    }
    query_string_update = urlencode(updated_payload)
    response = client.put(f"/customers/{customer_id}?{query_string_update}")
    assert response.status_code == 200
    assert response.json()["customer"]["name"] == username

def test_delete_customer():
    global customer_id
    response = client.delete(f"/customers/{customer_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Customer deleted successfully"
