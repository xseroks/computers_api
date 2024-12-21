import pytest
import requests
import time
from app import create_app
from app.database import get_session

@pytest.fixture
def base_url():
    """Фикстура для базового URL приложения"""
    return "http://localhost:5000"

@pytest.fixture
def app():
    """Фикстура для создания тестового приложения"""
    app = create_app('testing')
    return app

@pytest.fixture
def test_session():
    """Фикстура для создания тестовой сессии базы данных"""
    session = get_session()
    yield session
    # Очистка тестовых данных после каждого теста
    session.execute("TRUNCATE computers")
    session.execute("TRUNCATE configurations")

@pytest.fixture
def client(app):
    """Фикстура для создания тестового клиента"""
    return app.test_client() 