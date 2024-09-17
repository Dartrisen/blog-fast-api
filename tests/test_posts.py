from starlette import status

from routers.posts import get_db, get_current_user
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_posts(test_post):
    """Test retrieving a list of posts."""
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
    """Test retrieving a specific post by ID."""
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
    """Test retrieving a post that does not exist."""
    response = client.get("/posts/99")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Post not found"}


def test_create_post(test_post):
    """Test creating a new post."""
    request_data = {
        "content": "I still need to lock in...",
        "title": "Test Title number 2",
        "id": 2,
        "owner_id": 1,
        "published": True,
    }

    response = client.post("/posts/create_post", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(Post).filter(Post.id == 2).first()
    for key, value in request_data.items():
        assert getattr(model, key) == value


def test_update_post(test_post):
    """Test updating an existing post."""
    request_data = {
        "content": "Locked in...",
        "title": "Test Title number 3",
        "published": True,
    }

    response = client.put("/posts/1", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Post).filter(Post.id == 1).first()
    for key, value in request_data.items():
        assert getattr(model, key) == value


def test_update_post_not_found(test_post):
    """Test updating a post that does not exist."""
    request_data = {
        "content": "Locked in...",
        "title": "Test Title number 3",
        "published": True,
    }

    response = client.put("/posts/99", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Post not found"}


def test_delete_post(test_post):
    """Test deleting an existing post."""
    response = client.delete("/posts/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Post).filter(Post.id == 1).first()
    assert model is None


def test_delete_post_not_found():
    """Test deleting a post that does not exist."""
    response = client.delete("/posts/99")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Post not found"}
