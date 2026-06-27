"""
Інтеграційні тести для роутера автентифікації.
"""
def test_signup(client):
    response = client.post(
        "/auth/signup",
        json={"email": "new_user@example.com", "password": "password123"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "new_user@example.com"

def test_signup_duplicate(client):
    response = client.post(
        "/auth/signup",
        json={"email": "new_user@example.com", "password": "password123"}
    )
    assert response.status_code == 409

def test_login_unconfirmed(client):
    # Користувач створений, але confirmed=False (за замовчуванням)
    response = client.post(
        "/auth/login",
        data={"username": "new_user@example.com", "password": "password123"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Email not confirmed"

def test_forgot_password(client):
    response = client.post(
        "/auth/forgot-password",
        json={"email": "new_user@example.com"}
    )
    assert response.status_code == 200
    assert "message" in response.json()