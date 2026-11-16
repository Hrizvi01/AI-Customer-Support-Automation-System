import os
os.environ.setdefault('DATABASE_URL', 'sqlite://')
os.environ.setdefault('SENTIMENT_ENABLED', 'false')

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.config import settings


@pytest.fixture
def client(tmp_path, monkeypatch):
    engine = create_engine(f'sqlite:///{tmp_path / "test.db"}', connect_args={'check_same_thread': False})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    def override_db():
        with factory() as session:
            yield session
    monkeypatch.setattr(settings, 'model_dir', tmp_path / 'models')
    monkeypatch.setattr(settings, 'sentiment_dir', tmp_path / 'sentiment')
    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()
