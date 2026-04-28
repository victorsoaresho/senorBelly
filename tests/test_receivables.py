def test_create_receivable(client):
    payload = {
        "user_id": 1,
        "name": "Salário Mensal",
        "value": 5000.00,
        "due_date": "2026-12-05",
    }
    response = client.post("/receivables", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Salário Mensal"
    assert data["is_received"] is False


def test_get_receivables(client):
    response = client.get("/receivables")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_update_receivable(client):
    payload = {
        "user_id": 1,
        "name": "Venda de Item",
        "value": 100.00,
        "due_date": "2026-12-10",
    }
    post_res = client.post("/receivables", json=payload)
    receivable_id = post_res.get_json()["id"]

    response = client.put(f"/receivables/{receivable_id}", json={"is_received": True})
    assert response.status_code == 200
    assert response.get_json()["is_received"] is True


def test_delete_receivable(client):
    payload = {
        "user_id": 1,
        "name": "ToDeleteReceivable",
        "value": 50.00,
        "due_date": "2026-12-10",
    }
    post_res = client.post("/receivables", json=payload)
    receivable_id = post_res.get_json()["id"]

    response = client.delete(f"/receivables/{receivable_id}")
    assert response.status_code == 200

    get_res = client.get(f"/receivables/{receivable_id}")
    assert get_res.status_code == 404
