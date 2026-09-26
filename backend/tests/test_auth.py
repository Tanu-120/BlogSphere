def test_register_and_login(client):
    r = client.post("/api/auth/register", json={"name": "Bob", "email": "bob@example.com", "password": "supersecret"})
    assert r.status_code == 201
    assert r.json()["user"]["email"] == "bob@example.com"

    r2 = client.post("/api/auth/login", json={"email": "bob@example.com", "password": "supersecret"})
    assert r2.status_code == 200
    assert "access_token" in r2.json()


def test_login_wrong_password_fails(client):
    client.post("/api/auth/register", json={"name": "Carl", "email": "carl@example.com", "password": "correcthorse"})
    r = client.post("/api/auth/login", json={"email": "carl@example.com", "password": "wrongpass"})
    assert r.status_code == 401


def test_me_requires_auth(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401
