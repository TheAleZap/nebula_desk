def test_contact_crud(client):
    created = client.post("/contacts", json={"name": "Bob", "email": "bob@example.com"})
    assert created.status_code == 201
    contact_id = created.json()["id"]

    assert client.get(f"/contacts/{contact_id}").json()["name"] == "Bob"
    assert any(c["id"] == contact_id for c in client.get("/contacts").json())

    updated = client.put(
        f"/contacts/{contact_id}", json={"name": "Bobby", "email": "bob@example.com"}
    )
    assert updated.json()["name"] == "Bobby"

    assert client.delete(f"/contacts/{contact_id}").status_code == 204
    assert client.get(f"/contacts/{contact_id}").status_code == 404


def test_contact_validation(client):
    assert (
        client.post("/contacts", json={"name": "  ", "email": "x@example.com"}).status_code == 422
    )
    assert client.post("/contacts", json={"name": "X", "email": "not-an-email"}).status_code == 422


def test_cannot_delete_contact_with_conversations(client, conversation):
    response = client.delete(f"/contacts/{conversation['contact_id']}")
    assert response.status_code == 409
