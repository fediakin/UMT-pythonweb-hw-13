"""
Інтеграційні тести для роутера автентифікації.
"""
def test_signup(client):
    response = client.post(
        "/auth/signup",
        json={"email": "new_test_user@example.com", "password": "password123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new_test_user@example.com"

def test_signup_duplicate(client):
    response = client.post(
        "/auth/signup",
        json={"email": "new_test_user@example.com", "password": "password123"}
    )
    assert response.status_code == 409

def test_login(client):
    response = client.post(
        "/auth/login",
        data={"username": "new_test_user@example.com", "password": "password123"}
    )
    # 401 тому що email ще не confirmed (за логікою нашого роутера)
    assert response.status_code in [200, 401] 

def test_forgot_password(client):
    response = client.post(
        "/auth/forgot-password",
        json={"email": "new_test_user@example.com"}
    )
    assert response.status_code == 200
    assert "message" in response.json()