from flask import Flask
from config import config

def create_app(config_name='default'):
    app = Flask(__name__, template_folder='../templates')
    app.config.from_object(config[config_name])

    # Регистрация blueprints
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

# Создаем экземпляр приложения для использования в main.py
app = create_app('development')