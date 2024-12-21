from flask import render_template, redirect, url_for
from . import main
from app.database import session

@main.route('/')
def index():
    return render_template("index.html")

@main.route('/computers/configurations', methods=['GET'])
def show_combine_table():
    rows_computers = session.execute("SELECT * FROM computers")
    rows_confs = session.execute("SELECT * FROM configurations")
    
    confs_dict = {}
    for conf in rows_confs:
        key = (conf.brand, conf.department_number)
        confs_dict[key] = {
            'num_terminals': conf.num_terminals,
            'num_storage_devices': conf.num_storage_devices
        }
    
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

@main.errorhandler(400)
def error_400(error):
    return render_template('error.html'), 400 