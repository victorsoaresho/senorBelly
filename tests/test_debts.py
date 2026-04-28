def test_create_debt(client):
    payload = {
        "user_id": 1,
        "name": "Cartão de Crédito",
        "value": 1200.50,
        "maturity_date": "2026-12-01",
    }
    response = client.post("/debts", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Cartão de Crédito"
    assert data["value"] == 1200.50
    assert data["is_paid"] is False


def test_get_debts(client):
    response = client.get("/debts")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_update_debt(client):
    payload = {
        "user_id": 1,
        "name": "Conta de Água",
        "value": 50.00,
        "maturity_date": "2026-10-10",
    }
    post_res = client.post("/debts", json=payload)
    debt_id = post_res.get_json()["id"]

    response = client.put(f"/debts/{debt_id}", json={"is_paid": True})
    assert response.status_code == 200
    assert response.get_json()["is_paid"] is True


def test_delete_debt(client):
    payload = {
        "user_id": 1,
        "name": "ToDelete",
        "value": 10.00,
        "maturity_date": "2026-10-10",
    }
    post_res = client.post("/debts", json=payload)
    debt_id = post_res.get_json()["id"]

    response = client.delete(f"/debts/{debt_id}")
    assert response.status_code == 200

    get_res = client.get(f"/debts/{debt_id}")
    assert get_res.status_code == 404
