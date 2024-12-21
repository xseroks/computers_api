from flask import render_template, request, redirect, url_for
from . import main
from app.database import session

@main.route('/configurations', methods=['GET'])
def show_configurations():
    rows = session.execute("SELECT * FROM configurations")
    configurations = [{
        "brand": row.brand,
        "department_number": row.department_number,
        "num_terminals": row.num_terminals,
        "num_storage_devices": row.num_storage_devices
    } for row in rows]
    return render_template("configurations.html", configurations=configurations)

@main.route('/configurations/add', methods=['POST', 'GET'])
def add_configuration():
    if request.method == 'POST':
        data = request.form
        brand = data['brand']
        
        try:
            department_number = int(data['department_number'])
            num_terminals = int(data['num_terminals'])
            num_storage_devices = int(data['num_storage_devices'])
        except:
            return redirect(url_for('main.error_400'))

        if not (2 <= len(brand) <= 30 and 
                1 <= department_number <= 1000 and
                1 <= num_terminals <= 255 and
                1 <= num_storage_devices <= 255):
            return redirect(url_for('main.error_400'))

        session.execute(
            """
            INSERT INTO configurations (brand, department_number, num_terminals, num_storage_devices)
            VALUES (%s, %s, %s, %s)
            """,
            (brand, department_number, num_terminals, num_storage_devices))
        
        return redirect(url_for('main.show_configurations'))
    return render_template("add_configuration.html")

@main.route('/configurations/edit/<brand>/<department_number>', methods=['POST', 'GET'])
def edit_configuration(brand, department_number):
    if request.method == 'POST':
        try:
            num_terminals = int(request.form['num_terminals'])
            num_storage_devices = int(request.form['num_storage_devices'])
            
            if not (1 <= num_terminals <= 255 and 
                    1 <= num_storage_devices <= 255):
                return redirect(url_for('main.error_400'))
        except:
            return redirect(url_for('main.error_400'))
        
        session.execute(
            """
            UPDATE configurations 
            SET num_terminals = %s, num_storage_devices = %s 
            WHERE brand = %s AND department_number = %s
            """,
            (num_terminals, num_storage_devices, brand, int(department_number)))
        
        return redirect(url_for('main.show_configurations'))
    
    row = session.execute(
        """
        SELECT * FROM configurations 
        WHERE brand = %s AND department_number = %s
        """,
        (brand, int(department_number))).one()
    return render_template("edit_configuration.html", configuration=row)

@main.route('/configurations/delete/<brand>/<department_number>', methods=['POST'])
def delete_configuration(brand, department_number):
    session.execute(
        """
        DELETE FROM configurations 
        WHERE brand = %s AND department_number = %s
        """,
        (brand, int(department_number)))
    return redirect(url_for('main.show_configurations')) 