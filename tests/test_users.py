"""
Інтеграційні тести для роутера користувачів.
"""
def test_get_me(authorized_client):
    response = authorized_client.get("/users/me")
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_update_avatar_forbidden_for_user(authorized_client):
    # Тестовий юзер має Role.user, тому оновлення аватару має бути заборонено (403)
    response = authorized_client.patch(
        "/users/avatar",
        files={"file": ("test.jpg", b"fake image bytes", "image/jpeg")}
    )
    assert response.status_code == 403