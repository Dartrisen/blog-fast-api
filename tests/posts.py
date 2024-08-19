from starlette import status

from routers.posts import get_db, get_current_user
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_posts(test_post):
    response = client.get("/posts/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        "content": "I need to lock in...",
        "title": "Test Title",
        "id": 1,
        "owner_id": 1,
        "published": True,
    }]


def test_get_post(test_post):
    response = client.get("/posts/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "content": "I need to lock in...",
        "title": "Test Title",
        "id": 1,
        "owner_id": 1,
        "published": True,
    }


def test_get_post_not_found(test_post):
    response = client.get("/posts/99")
    assert response.status_code == 404
    assert response.json() == {"detail": "Post not found"}


def test_create_post(test_post):
    request_data = {
        "content": "I still need to lock in...",
        "title": "Test Title number 2",
        "id": 2,
        "owner_id": 1,
        "published": True,
    }

    response = client.post("/posts/create_post", json=request_data)
    assert response.status_code == 201

    db = TestingSessionLocal()
    model = db.query(Post).filter(Post.id == 2).first()
    for key, value in request_data.items():
        assert getattr(model, key) == value


def test_update_post(test_post):
    request_data = {
        "content": "Locked in...",
        "title": "Test Title number 3",
        "published": True,
    }

    response = client.put("/posts/1", json=request_data)
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Post).filter(Post.id == 1).first()
    for key, value in request_data.items():
        assert getattr(model, key) == value


def test_update_post_not_found(test_post):
    request_data = {
        "content": "Locked in...",
        "title": "Test Title number 3",
        "published": True,
    }

    response = client.put("/posts/99", json=request_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Post not found"}
