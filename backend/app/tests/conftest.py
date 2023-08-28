import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database
from fastapi.testclient import TestClient
from app.config import TEST_DB_URI
from app.main import app
from app.dependencies import get_db
from app.models import Base

engine = create_engine(TEST_DB_URI)


def get_test_db():
    SessionLocal = sessionmaker(bind=engine)
    test_db = SessionLocal()

    try:
        yield test_db

    finally:
        test_db.close()


@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    if database_exists(engine.url):
        drop_database(engine.url)

    create_database(engine.url)
    Base.metadata.create_all(bind=engine)

    app.dependency_overrides[get_db] = get_test_db

    yield  # run tests

    drop_database(engine.url)


@pytest.fixture(autouse=True)
def test_db_session():
    SessionLocal = sessionmaker(bind=engine)

    session = SessionLocal()
    yield session

    session.close()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
