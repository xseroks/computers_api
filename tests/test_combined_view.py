import pytest
import requests
import time

def test_combined_view(base_url):
    """Тест комбинированного представления компьютеров и конфигураций"""
    test_computer = {
        "serial_number": "COMB123",
        "brand": "CombBrand",
        "department_number": "1"
    }
    test_config = {
        "brand": "CombBrand",
        "department_number": "1",
        "num_terminals": "2",
        "num_storage_devices": "3"
    }
    
    try:
        # Добавление тестовых данных
        response = requests.post(f"{base_url}/computers/add", data=test_computer)
        assert response.status_code == 200
        
        response = requests.post(f"{base_url}/configurations/add", data=test_config)
        assert response.status_code == 200
        
        # Небольшая задержка для гарантии записи данных
        time.sleep(1)
        
        # Проверка комбинированного представления
        response = requests.get(f"{base_url}/computers/configurations")
        assert response.status_code == 200
        
        # Проверка наличия всех данных
        response_text = response.text.lower()
        assert all(x in response_text for x in [
            "comb123",
            "combbrand",
            "1",  # department_number
            "2",  # num_terminals
            "3"   # num_storage_devices
        ])
    finally:
        # Очистка тестовых данных
        requests.post(f"{base_url}/computers/delete/COMB123")
        requests.post(f"{base_url}/configurations/delete/CombBrand/1")

def test_combined_view_with_missing_configuration(base_url):
    """Тест комбинированного представления с отсутствующей конфигурацией"""
    test_computer = {
        "serial_number": "NOCFG123",
        "brand": "NoCfgBrand",
        "department_number": "1"
    }
    
    try:
        # Добавление только компьютера
        response = requests.post(f"{base_url}/computers/add", data=test_computer)
        assert response.status_code == 200
        
        # Проверка комбинированного представления
        response = requests.get(f"{base_url}/computers/configurations")
        assert response.status_code == 200
        assert "NOCFG123" in response.text
        assert "NoCfgBrand" in response.text
    finally:
        # Очистка
        requests.post(f"{base_url}/computers/delete/NOCFG123")