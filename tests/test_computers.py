import pytest
import requests

def test_get_computers(base_url):
    """Тест получения списка компьютеров"""
    response = requests.get(f"{base_url}/computers")
    assert response.status_code == 200
    assert "computers" in response.text

def test_add_computer(base_url):
    """Тест добавления компьютера"""
    test_computer = {
        "serial_number": "TEST123",
        "brand": "TestBrand",
        "department_number": "1"
    }
    
    # Добавление компьютера
    response = requests.post(f"{base_url}/computers/add", data=test_computer)
    assert response.status_code == 200
    
    # Проверка, что компьютер добавлен
    response = requests.get(f"{base_url}/computers")
    assert "TEST123" in response.text
    assert "TestBrand" in response.text
    
    # Очистка - удаление тестового компьютера
    requests.post(f"{base_url}/computers/delete/TEST123")

def test_edit_computer(base_url):
    """Тест редактирования компьютера"""
    # Сначала добавим тестовый компьютер
    test_computer = {
        "serial_number": "TEST456",
        "brand": "TestBrand",
        "department_number": "1"
    }
    requests.post(f"{base_url}/computers/add", data=test_computer)
    
    # Редактирование
    edit_data = {
        "department_number": "2"
    }
    response = requests.post(f"{base_url}/computers/edit/TEST456", data=edit_data)
    assert response.status_code == 200
    
    # Проверка изменений
    response = requests.get(f"{base_url}/computers")
    assert "TEST456" in response.text
    assert "2" in response.text
    
    # Очистка
    requests.post(f"{base_url}/computers/delete/TEST456")

def test_delete_computer(base_url):
    """Тест удаления компьютера"""
    # Добавление тестового компьютера
    test_computer = {
        "serial_number": "TEST789",
        "brand": "TestBrand",
        "department_number": "1"
    }
    requests.post(f"{base_url}/computers/add", data=test_computer)
    
    # Удаление
    response = requests.post(f"{base_url}/computers/delete/TEST789")
    assert response.status_code == 200
    
    # Проверка, что компью��ер удален
    response = requests.get(f"{base_url}/computers")
    assert "TEST789" not in response.text

def test_search_computers(base_url):
    """Тест поиска компьютеров"""
    # Добавление тестового компьютера
    test_computer = {
        "serial_number": "SEARCH123",
        "brand": "SearchBrand",
        "department_number": "1"
    }
    requests.post(f"{base_url}/computers/add", data=test_computer)
    
    # Поиск
    response = requests.get(f"{base_url}/computers/search?brand=SearchBrand")
    assert response.status_code == 200
    assert "SEARCH123" in response.text
    
    # Очистка
    requests.post(f"{base_url}/computers/delete/SEARCH123") 