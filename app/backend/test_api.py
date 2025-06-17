import requests
import json

BASE_URL = "http://localhost:8000"

def test_register():
    # Test valid registration
    valid_user = {
        "email": "test@hr.nl",
        "password": "test123",
        "display_name": "Test User"
    }
    response = requests.post(f"{BASE_URL}/register", json=valid_user)
    print("Register (valid):", response.status_code, response.json())

    # Test invalid email
    invalid_email = {
        "email": "test@gmail.com",
        "password": "test123",
        "display_name": "Test User"
    }
    response = requests.post(f"{BASE_URL}/register", json=invalid_email)
    print("Register (invalid email):", response.status_code, response.json())

def test_login():
    # Test valid login
    valid_credentials = {
        "email": "test@hr.nl",
        "password": "test123"
    }
    response = requests.post(f"{BASE_URL}/login", json=valid_credentials)
    print("Login (valid):", response.status_code, response.json())

    # Test invalid password
    invalid_password = {
        "email": "test@hr.nl",
        "password": "wrongpassword"
    }
    response = requests.post(f"{BASE_URL}/login", json=invalid_password)
    print("Login (invalid password):", response.status_code, response.json())

if __name__ == "__main__":
    print("Testing API endpoints...")
    test_register()
    test_login() 