from flask import Flask
from flask import render_template

app = Flask(__name__, template_folder='../templates')

@app.route('/test/<name>')
def index(name):
    return render_template('index.html', name=name)