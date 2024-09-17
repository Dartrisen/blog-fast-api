import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from main import app
from models import Post, User
from routers.auth import get_password_hash

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override the dependency to provide a test database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    """Override the dependency to return a mock current user."""
    return {"username": "dartrisen", "id": 1, "is_superuser": True}


def override_get_current_non_superuser():
    """Override the dependency to return a mock non-superuser."""
    return {"username": "dartrisen", "id": 1, "is_superuser": False}


client = TestClient(app)


@pytest.fixture
def test_post():
    """Fixture for creating a test post in the database.

    This fixture creates a sample post, adds it to the database, and yields it for use in tests.
    After the test, it cleans up by deleting all posts from the database.

    :return: The created Post object.

    :raises AssertionError: If there are issues with database operations.
    """
    post = Post(
        title="Test Title",
        content="I need to lock in...",
        published=True,
        owner_id=1
    )

    db = TestingSessionLocal()
    db.add(post)
    db.commit()
    db.refresh(post)
    yield post
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM posts;"))
        connection.commit()


@pytest.fixture
def test_user():
    """Fixture for creating a test user in the database.

    This fixture creates a sample user, adds it to the database, and yields it for use in tests.
    After the test, it cleans up by deleting all users from the database.

    :return: The created User object.

    :raises AssertionError: If there are issues with database operations.
    """
    user = User(
        username="dartrisen",
        email="test@test.com",
        hashed_password=get_password_hash("testpassword"),
        is_superuser=True,
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()
