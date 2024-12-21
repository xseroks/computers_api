from flask import render_template, request, redirect, url_for
from . import main
from app.database import session

@main.route('/computers/search', methods=['GET'])
def search_computers():
    brand = request.args.get('brand')
    if not brand:
        return redirect(url_for('main.show_computers'))
    
    rows = session.execute("SELECT * FROM computers WHERE brand = %s ALLOW FILTERING", (brand,))
    computers = [
        {
            "serial_number": row.serial_number,
            "brand": row.brand,
            "department_number": row.department_number
        } for row in rows
    ]
    return render_template("computers.html", computers=computers)

@main.route('/computers', methods=['GET'])
def show_computers():
    rows = session.execute("SELECT * FROM computers")
    computers = [
        {
            "serial_number": row.serial_number,
            "brand": row.brand,
            "department_number": row.department_number
        } for row in rows
    ]
    return render_template("computers.html", computers=computers)

@main.route('/computers/add', methods=['POST', 'GET'])
def add_computer():
    if request.method == 'POST':
        data = request.form
        serial_number = data['serial_number']
        brand = data['brand']

        try:
            department_number = int(data['department_number'])
        except:
            return redirect(url_for('main.error_400'))

        if not (2 <= len(serial_number) <= 50 and 
                2 <= len(brand) <= 30 and 
                1 <= department_number <= 1000):
            return redirect(url_for('main.error_400'))

        session.execute(
            """
            INSERT INTO computers (serial_number, brand, department_number)
            VALUES (%s, %s, %s)
            """,
            (serial_number, brand, department_number))
        
        return redirect(url_for('main.show_computers'))
    
    return render_template("add_computer.html")

@main.route('/computers/edit/<serial_number>', methods=['POST', 'GET'])
def edit_computer(serial_number):
    if request.method == 'POST':
        try:
            new_department_number = int(request.form['department_number'])
            if not (1 <= new_department_number <= 255):
                return redirect(url_for('main.error_400'))
        except:
            return redirect(url_for('main.error_400'))
                
        session.execute(
            """
            UPDATE computers SET department_number = %s WHERE serial_number = %s
            """,
            (new_department_number, serial_number)
        )
        return redirect(url_for('main.show_computers'))
    
    row = session.execute("SELECT * FROM computers WHERE serial_number = %s", (serial_number,)).one()
    return render_template("edit_computer.html", computer=row)

@main.route('/computers/delete/<serial_number>', methods=['POST'])
def delete_computer(serial_number):
    session.execute("DELETE FROM computers WHERE serial_number = %s", (serial_number,))
    return redirect(url_for('main.show_computers')) 