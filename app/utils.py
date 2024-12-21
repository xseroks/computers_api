def validate_computer_data(serial_number, brand, department_number):
    """Валидация данных компьютера"""
    if not (2 <= len(serial_number) <= 50):
        return False
    if not (2 <= len(brand) <= 30):
        return False
    if not (1 <= department_number <= 1000):
        return False
    return True

def validate_configuration_data(brand, department_number, num_terminals, num_storage_devices):
    """Валидация данных конфигурации"""
    if not (2 <= len(brand) <= 30):
        return False
    if not (1 <= department_number <= 1000):
        return False
    if not (1 <= num_terminals <= 255):
        return False
    if not (1 <= num_storage_devices <= 255):
        return False
    return True 