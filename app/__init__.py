from flask import Flask, jsonify, request, render_template, redirect, url_for
from cassandra.cluster import Cluster
import time
import json

app = Flask(__name__, template_folder='../templates')

with open('conf.json', 'r') as f:
    data = json.load(f)
    
HOST = data['cassandra']['host']
PORT = data['cassandra']['port']

# Подключение к Cassandra
while True:
    try:
        cluster = Cluster([HOST], port=PORT)
        session = cluster.connect()
        print("Connected to Cassandra!")
        break
    except Exception as e:
        print(f"Connection failed: {e}. Retrying...")
        time.sleep(5)

# Создаем keyspace
KEYSPACE = "my_keyspace"
try:
    session.execute(f"""
        CREATE KEYSPACE {KEYSPACE}
        WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': '1' }}
    """)
    print(f"Keyspace '{KEYSPACE}' создан успешно.")
except Exception as e:
    print(f"Ошибка при создании keyspace: {e}")

# Устанавливаем созданный keyspace для дальнейшей работы
session.set_keyspace(KEYSPACE)

# Создание таблиц, если они еще не существуют
session.execute("""
    CREATE TABLE IF NOT EXISTS computers (
        serial_number text PRIMARY KEY,
        brand text,
        department_number int
    )
""")

session.execute("""
    CREATE TABLE IF NOT EXISTS configurations (
        brand text,
        department_number int,
        num_terminals int,
        num_storage_devices int,
        PRIMARY KEY (brand, department_number)
    )
""")

@app.route('/', methods=['GET'])
def show_index():
    return render_template("index.html")

@app.route('/computers/search', methods=['GET'])
def search_computers():
    brand = request.args.get('brand')
    if not brand:
        return redirect(url_for('show_computers'))
    
    rows = session.execute("SELECT * FROM computers WHERE brand = %s ALLOW FILTERING", (brand,))
    computers = [
        {
            "serial_number": row.serial_number,
            "brand": row.brand,
            "department_number": row.department_number
        } for row in rows
    ]
    return render_template("computers.html", computers=computers)

@app.route('/computers/configurations', methods=['GET'])
def show_combine_table():
    # Получение всех записей из таблиц
    rows_computers = session.execute("SELECT * FROM computers")
    rows_confs = session.execute("SELECT * FROM configurations")
    
    # Преобразуем конфигурации в словарь для быстрого поиска
    confs_dict = {}
    for conf in rows_confs:
        key = (conf.brand, conf.department_number)
        confs_dict[key] = {
            'num_terminals': conf.num_terminals,
            'num_storage_devices': conf.num_storage_devices
        }
    
    # Объединяем данные
    combined_data = []
    for computer in rows_computers:
        key = (computer.brand, computer.department_number)
        conf = confs_dict.get(key, {'num_terminals': None, 'num_storage_devices': None})
        
        combined_row = {
            'serial_number': computer.serial_number,
            'brand': computer.brand,
            'department_number': computer.department_number,
            'num_terminals': conf['num_terminals'],
            'num_storage_devices': conf['num_storage_devices']
        }
        combined_data.append(combined_row)
    
    return render_template("combine_res.html", rows=combined_data)

# Маршрут для отображения списка компьютеров
@app.route('/computers', methods=['GET'])
def show_computers():
    rows = session.execute("SELECT * FROM computers")
    
    computers = [
        {
            "serial_number"         : row.serial_number,
            "brand"                 : row.brand,
            "department_number"     : row.department_number
        } for row in rows
    ]

    return render_template("computers.html", computers=computers)

# Маршрут для добавления компьютера
@app.route('/computers/add', methods=['POST', 'GET'])
def add_computer():
    if request.method == 'POST':
        data = request.form
        serial_number = data['serial_number']
        brand = data['brand']

        try:
            department_number = int(data['department_number'])
        except Exception as e:
            return redirect(url_for('error_400'))

        if len(serial_number) > 50 or len(serial_number) < 2:
            return redirect(url_for('error_400'))

        if len(brand) > 30 or len(brand) < 2:
            return redirect(url_for('error_400'))

        if department_number < 1 or department_number > 1000:
            return redirect(url_for('error_400'))

        session.execute(
            """
            INSERT INTO computers (serial_number, brand, department_number)
            VALUES (%s, %s, %s)
            """,
            (serial_number, brand, department_number))
        
        return redirect(url_for('show_computers'))
    
    return render_template("add_computer.html")

# Маршрут для обновления компьютера
@app.route('/computers/edit/<serial_number>', methods=['POST', 'GET'])
def edit_computer(serial_number):
    if request.method == 'POST':
        
        try:
            new_department_number = int(request.form['department_number'])
        except Exception as e:
            return redirect(url_for('error_400'))
        
        if new_department_number < 1 or new_department_number > 255:
            return redirect(url_for('error_400'))
                
        session.execute(
            """
            UPDATE computers SET department_number = %s WHERE serial_number = %s
            """,
            (new_department_number, serial_number)
        )
        print("[INFO] Update computers")
        return redirect(url_for('show_computers'))
    
    row = session.execute("SELECT * FROM computers WHERE serial_number = %s", (serial_number,)).one()
    return render_template("edit_computer.html", computer=row)

# Маршрут для удаления компьютера
@app.route('/computers/delete/<serial_number>', methods=['POST'])
def delete_computer(serial_number):
    session.execute("DELETE FROM computers WHERE serial_number = %s", (serial_number,))
    return redirect(url_for('show_computers'))

# Маршрут для отображения списка конфигураций
@app.route('/configurations', methods=['GET'])
def show_configurations():
    rows = session.execute("SELECT * FROM configurations")
    configurations = [{"brand": row.brand, "department_number": row.department_number, "num_terminals": row.num_terminals, "num_storage_devices": row.num_storage_devices} for row in rows]
    return render_template("configurations.html", configurations=configurations)

# Маршрут для добавления конфигурации
@app.route('/configurations/add', methods=['POST', 'GET'])
def add_configuration():
    if request.method == 'POST':
        data = request.form
        brand = data['brand']
        
        try:
            department_number = int(data['department_number'])
        except Exception as e:
            return redirect(url_for('error_400'))

        try:
            num_terminals = int(data['num_terminals'])
        except Exception as e:
            return redirect(url_for('error_400'))

        try:
            num_storage_devices = int(data['num_storage_devices'])
        except Exception as e:
            return redirect(url_for('error_400'))

        if len(brand) > 30 or len(brand) < 2:
            return redirect(url_for('error_400'))

        if department_number < 1 or department_number > 1000:
            return redirect(url_for('error_400'))

        if num_terminals < 1 or num_terminals > 255:
            return redirect(url_for('error_400'))        

        if num_storage_devices < 1 or num_storage_devices > 255:
            return redirect(url_for('error_400'))        

        session.execute("""
            INSERT INTO configurations (brand, department_number, num_terminals, num_storage_devices)
            VALUES (%s, %s, %s, %s)
        """, (brand, department_number, num_terminals, num_storage_devices))
        
        return redirect(url_for('show_configurations'))
    return render_template("add_configuration.html")

# Маршрут для обновления конфигурации
@app.route('/configurations/edit/<brand>/<department_number>', methods=['POST', 'GET'])
def edit_configuration(brand, department_number):
    if request.method == 'POST':
        try:
            num_terminals = int(data['num_terminals'])
        except Exception as e:
            return redirect(url_for('error_400'))

        try:
            num_storage_devices = int(data['num_storage_devices'])
        except Exception as e:
            return redirect(url_for('error_400'))

        if num_terminals < 1 or num_terminals > 255:
            return redirect(url_for('error_400'))        

        if num_storage_devices < 1 or num_storage_devices > 255:
            return redirect(url_for('error_400'))        
        
        
        session.execute("""
            UPDATE configurations 
            SET num_terminals = %s, num_storage_devices = %s 
            WHERE brand = %s AND department_number = %s
        """, (num_terminals, num_storage_devices, brand, int(department_number)))
        
        return redirect(url_for('show_configurations'))
    
    row = session.execute("SELECT * FROM configurations WHERE brand = %s AND department_number = %s", (brand, int(department_number))).one()
    return render_template("edit_configuration.html", configuration=row)

# Маршрут для удаления конфигурации
@app.route('/configurations/delete/<brand>/<department_number>', methods=['POST'])
def delete_configuration(brand, department_number):
    session.execute("""
        DELETE FROM configurations WHERE brand = %s AND department_number = %s
    """, (brand, int(department_number)))
    return redirect(url_for('show_configurations'))

# Обработчик ошибки 400
@app.errorhandler(400)
def error_400(error):
    return render_template('error.html'), 400