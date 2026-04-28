def test_create_user(client):
    payload = {
        "name": "Test User",
        "email": "test@test.com",
        "password": "password123"
    }
    response = client.post('/users', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == "Test User"
    assert data['email'] == "test@test.com"
    assert "id" in data

def test_get_users(client):
    response = client.get('/users')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_update_user(client):
    # Setup: Cria um usuário primeiro
    post_res = client.post('/users', json={"name": "Old", "email": "old@test.com", "password": "123"})
    user_id = post_res.get_json()['id']

    # Atualiza o usuário
    response = client.put(f'/users/{user_id}', json={"name": "New Name"})
    assert response.status_code == 200
    assert response.get_json()['name'] == "New Name"

def test_delete_user(client):
    post_res = client.post('/users', json={"name": "Del", "email": "del@test.com", "password": "123"})
    user_id = post_res.get_json()['id']

    response = client.delete(f'/users/{user_id}')
    assert response.status_code == 200

    # Verifica se foi deletado
    get_res = client.get(f'/users/{user_id}')
    assert get_res.status_code == 404
