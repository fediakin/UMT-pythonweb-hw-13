"""
Інтеграційні тести для роутера користувачів.
"""
def test_get_me(authorized_client):
    response = authorized_client.get("/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "role" in data

def test_update_avatar_forbidden_for_user(authorized_client):
    # Тестовий юзер має роль Role.user, тому оновлення аватару має бути заборонено
    with open("requirements.txt", "rb") as f:
        response = authorized_client.patch(
            "/users/avatar",
            files={"file": ("requirements.txt", f, "text/plain")}
        )
    assert response.status_code == 403