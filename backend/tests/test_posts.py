from tests.conftest import register_and_login


def test_anonymous_can_list_and_read_published_posts(client):
    headers = register_and_login(client, "dana@example.com", "Dana")
    create = client.post(
        "/api/posts",
        data={"title": "Hello World", "content": "This is my first post.", "status": "published"},
        headers=headers,
    )
    assert create.status_code == 201
    slug = create.json()["slug"]

    # No auth headers here - simulating an anonymous visitor.
    listing = client.get("/api/posts")
    assert listing.status_code == 200
    assert listing.json()["total"] >= 1

    detail = client.get(f"/api/posts/{slug}")
    assert detail.status_code == 200
    assert detail.json()["title"] == "Hello World"


def test_only_owner_or_admin_can_edit_post(client):
    headers_owner = register_and_login(client, "eve@example.com", "Eve")
    headers_other = register_and_login(client, "frank@example.com", "Frank")

    create = client.post(
        "/api/posts",
        data={"title": "Eves Post", "content": "content", "status": "published"},
        headers=headers_owner,
    )
    post_id = create.json()["id"]

    forbidden = client.put(f"/api/posts/{post_id}", json={"title": "Hacked"}, headers=headers_other)
    assert forbidden.status_code == 403

    allowed = client.put(f"/api/posts/{post_id}", json={"title": "Updated by Eve"}, headers=headers_owner)
    assert allowed.status_code == 200
    assert allowed.json()["title"] == "Updated by Eve"


def test_anonymous_cannot_create_post(client):
    r = client.post("/api/posts", data={"title": "No Auth", "content": "x", "status": "draft"})
    assert r.status_code == 401


def test_like_and_comment_require_auth_but_reading_does_not(client):
    headers = register_and_login(client, "gina@example.com", "Gina")
    create = client.post(
        "/api/posts",
        data={"title": "Likeable Post", "content": "content", "status": "published"},
        headers=headers,
    )
    post_id = create.json()["id"]

    anon_like = client.post(f"/api/posts/{post_id}/like")
    assert anon_like.status_code == 401

    liked = client.post(f"/api/posts/{post_id}/like", headers=headers)
    assert liked.status_code == 200
    assert liked.json()["liked"] is True

    anon_read_comments = client.get(f"/api/posts/{post_id}/comments")
    assert anon_read_comments.status_code == 200

    anon_comment = client.post(f"/api/posts/{post_id}/comments", json={"content": "hi"})
    assert anon_comment.status_code == 401

    commented = client.post(f"/api/posts/{post_id}/comments", json={"content": "Nice post!"}, headers=headers)
    assert commented.status_code == 201


def test_ai_generate_fallback_when_no_provider(client):
    headers = register_and_login(client, "hank@example.com", "Hank")
    create = client.post(
        "/api/posts",
        data={"title": "AI Test", "content": "Artificial intelligence is transforming software engineering rapidly.", "status": "draft"},
        headers=headers,
    )
    post_id = create.json()["id"]
    r = client.post(f"/api/posts/{post_id}/ai/generate", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["source"] == "fallback"
    assert len(body["ai_summary"]) > 0


def test_search_matches_a_misspelled_word(client):
    headers = register_and_login(client, "iris@example.com", "Iris")
    client.post(
        "/api/posts",
        data={"title": "Database indexes keep the feed fast", "content": "An index avoids a full table scan.", "status": "published"},
        headers=headers,
    )
    found = client.get("/api/posts", params={"search": "indxes"})
    assert found.status_code == 200
    body = found.json()
    titles = [item["title"] for item in body["items"]]
    assert "Database indexes keep the feed fast" in titles
    assert body["search_models"] == ["BM25", "TF-IDF", "Naive Bayes", "LSA"]


def test_a_view_is_counted_once_per_person(client):
    author = register_and_login(client, "vera@example.com", "Vera")
    reader = register_and_login(client, "wes@example.com", "Wes")
    create = client.post(
        "/api/posts",
        data={"title": "Counted once", "content": "A published note.", "status": "published"},
        headers=author,
    )
    slug = create.json()["slug"]

    author_open = client.get(f"/api/posts/{slug}", headers=author)
    assert author_open.json()["view_count"] == 0

    first = client.get(f"/api/posts/{slug}", headers={**reader, "X-Reader": "wes-browser"})
    second = client.get(f"/api/posts/{slug}", headers={**reader, "X-Reader": "wes-browser"})
    assert first.json()["view_count"] == 1
    assert second.json()["view_count"] == 1

    guest = client.get(f"/api/posts/{slug}", headers={"X-Reader": "guest-browser"})
    assert guest.json()["view_count"] == 2
    guest_again = client.get(f"/api/posts/{slug}", headers={"X-Reader": "guest-browser"})
    assert guest_again.json()["view_count"] == 2


def test_draft_is_visible_only_to_its_author(client):
    author = register_and_login(client, "nina@example.com", "Nina")
    other = register_and_login(client, "omar@example.com", "Omar")
    create = client.post(
        "/api/posts",
        data={"title": "Private draft", "content": "Not ready.", "status": "draft"},
        headers=author,
    )
    slug = create.json()["slug"]
    post_id = create.json()["id"]

    assert client.get(f"/api/posts/{slug}", headers=author).status_code == 200
    assert client.get(f"/api/posts/{slug}").status_code == 404
    assert client.get(f"/api/posts/{slug}", headers=other).status_code == 404

    from app.database import SessionLocal
    from app.models.user import User, UserRole

    db = SessionLocal()
    omar = db.query(User).filter(User.email == "omar@example.com").one()
    omar.role = UserRole.ADMIN
    db.commit()
    db.close()

    assert client.get(f"/api/posts/{slug}", headers=other).status_code == 404
    assert client.delete(f"/api/admin/posts/{post_id}", headers=other).status_code == 404


def test_comment_with_a_threat_is_blocked(client):
    headers = register_and_login(client, "jade@example.com", "Jade")
    create = client.post(
        "/api/posts",
        data={"title": "Open thread", "content": "Say something useful.", "status": "published"},
        headers=headers,
    )
    post_id = create.json()["id"]
    blocked = client.post(f"/api/posts/{post_id}/comments", json={"content": "kill yourself"}, headers=headers)
    assert blocked.status_code == 422
