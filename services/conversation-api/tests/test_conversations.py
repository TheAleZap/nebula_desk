def test_conversation_crud(client, conversation):
    conversation_id = conversation["id"]
    assert conversation["status"] == "open"
    assert conversation["messages"][0]["sender"] == "customer"

    detail = client.get(f"/conversations/{conversation_id}").json()
    assert detail["contact"]["name"] == "Ana Test"

    updated = client.put(
        f"/conversations/{conversation_id}",
        json={"status": "pending", "assigned_agent_id": 1, "subject": "Refund (urgent)"},
    ).json()
    assert updated["status"] == "pending"
    assert updated["agent"]["name"] == "Demo Agent"
    assert updated["subject"] == "Refund (urgent)"

    unassigned = client.put(f"/conversations/{conversation_id}", json={"unassign": True}).json()
    assert unassigned["assigned_agent_id"] is None

    assert client.delete(f"/conversations/{conversation_id}").status_code == 204
    assert client.get(f"/conversations/{conversation_id}").status_code == 404


def test_conversation_validation(client, contact, conversation):
    assert (
        client.post("/conversations", json={"contact_id": 99999, "subject": "x"}).status_code == 400
    )
    assert (
        client.post(
            "/conversations", json={"contact_id": contact["id"], "subject": " "}
        ).status_code
        == 422
    )
    assert (
        client.put(
            f"/conversations/{conversation['id']}", json={"assigned_agent_id": 999}
        ).status_code
        == 400
    )
    assert (
        client.put(f"/conversations/{conversation['id']}", json={"subject": "  "}).status_code
        == 422
    )


def test_list_filters_and_search(client, conversation):
    assert any(c["id"] == conversation["id"] for c in client.get("/conversations").json())
    assert client.get("/conversations", params={"q": "refund"}).json()
    assert client.get("/conversations", params={"q": "zzz-no-match"}).json() == []
    assert all(
        c["status"] == "open"
        for c in client.get("/conversations", params={"status": "open"}).json()
    )
    client.put(f"/conversations/{conversation['id']}", json={"assigned_agent_id": 2})
    mine = client.get("/conversations", params={"assigned_agent_id": 2}).json()
    assert [c["id"] for c in mine] == [conversation["id"]]


def test_agent_reply_sets_first_response(client, conversation):
    response = client.post(
        f"/conversations/{conversation['id']}/messages",
        json={"sender": "agent", "body": "Sorry, refunding now", "from_suggestion": True},
    )
    assert response.status_code == 201
    detail = client.get(f"/conversations/{conversation['id']}").json()
    assert detail["first_response_at"] is not None
    assert len(detail["messages"]) == 2


def test_unknown_conversation_is_404(client):
    assert client.get("/conversations/424242").status_code == 404
    assert (
        client.post(
            "/conversations/424242/messages", json={"sender": "agent", "body": "hi"}
        ).status_code
        == 404
    )


def test_simulate_creates_a_customer_conversation(client):
    response = client.post("/conversations/simulate")
    assert response.status_code == 201
    conversation = response.json()["conversation"]
    assert conversation["status"] == "open"
    detail = client.get(f"/conversations/{conversation['id']}").json()
    assert detail["messages"][0]["sender"] == "customer"
