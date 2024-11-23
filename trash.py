from flask import Flask, jsonify, request, render_template, redirect, url_for
from cassandra.cluster import Cluster

app = Flask(__name__)

# Подключение к Cassandra
cluster = Cluster(['127.0.0.1'])
session = cluster.connect()

# Подключение к Keyspace и создание его при необходимости
try:
    session.set_keyspace('my_keyspace')
except Exception as ex:
    print(ex)

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

# Маршрут для отображения списка компьютеров
@app.route('/computers', methods=['GET'])
def show_computers():
    rows = session.execute("SELECT * FROM computers")
    computers = [{"serial_number": row.serial_number, "brand": row.brand, "department_number": row.department_number} for row in rows]
    return render_template("computers.html", computers=computers)

# Маршрут для добавления компьютера
@app.route('/computers/add', methods=['POST', 'GET'])
def add_computer():
    if request.method == 'POST':
        data = request.form
        serial_number = data['serial_number']
        brand = data['brand']
        department_number = int(data['department_number'])
        
        session.execute("""
            INSERT INTO computers (serial_number, brand, department_number)
            VALUES (%s, %s, %s)
        """, (serial_number, brand, department_number))
        
        return redirect(url_for('show_computers'))
    return render_template("add_computer.html")

# Маршрут для обновления компьютера
@app.route('/computers/edit/<serial_number>', methods=['POST', 'GET'])
def edit_computer(serial_number):
    if request.method == 'POST':
        new_department_number = int(request.form['department_number'])
        session.execute("""
            UPDATE computers SET department_number = %s WHERE serial_number = %s
        """, (new_department_number, serial_number))
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
        department_number = int(data['department_number'])
        num_terminals = int(data['num_terminals'])
        num_storage_devices = int(data['num_storage_devices'])
        
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
        num_terminals = int(request.form['num_terminals'])
        num_storage_devices = int(request.form['num_storage_devices'])
        
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

# Запуск сервера
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
