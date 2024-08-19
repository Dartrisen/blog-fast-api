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
