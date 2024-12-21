class Config:
    DEBUG = False
    SECRET_KEY = 'ваш-секретный-ключ-здесь'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': Config,
    'default': DevelopmentConfig
} 