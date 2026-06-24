def test_create_contact(authorized_client):
    response = authorized_client.post(
        "/contacts/",
        json={
            "first_name": "Ivan",
            "last_name": "Franko",
            "email": "ivan@franko.com",
            "phone": "+380123456789",
            "birthday": "1856-08-27"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Ivan"
    assert "id" in data


def test_create_contact_duplicate_email(authorized_client):
    response = authorized_client.post(
        "/contacts/",
        json={
            "first_name": "Ivan",
            "last_name": "Franko",
            "email": "ivan@franko.com",
            "phone": "+380999999999",
            "birthday": "1856-08-27"
        },
    )
    assert response.status_code == 409


def test_get_contacts(authorized_client):
    response = authorized_client.get("/contacts/")
    assert response.status_code == 200
    data = response.json()
    assert type(data) == list
    assert len(data) > 0


def test_get_contact_by_id(authorized_client):
    contacts = authorized_client.get("/contacts/").json()
    contact_id = contacts[0]["id"]
    
    response = authorized_client.get(f"/contacts/{contact_id}")
    assert response.status_code == 200
    assert response.json()["id"] == contact_id


def test_update_contact(authorized_client):
    contacts = authorized_client.get("/contacts/").json()
    contact_id = contacts[0]["id"]
    
    response = authorized_client.put(
        f"/contacts/{contact_id}",
        json={
            "first_name": "Updated",
            "last_name": "Name",
            "email": "ivan@franko.com",
            "phone": "+380000000000",
            "birthday": "1856-08-27"
        },
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Updated"


def test_delete_contact(authorized_client):
    contacts = authorized_client.get("/contacts/").json()
    contact_id = contacts[0]["id"]
    
    response = authorized_client.delete(f"/contacts/{contact_id}")
    assert response.status_code == 204
    
    response_check = authorized_client.get(f"/contacts/{contact_id}")
    assert response_check.status_code == 404