import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    TESTENV_MONGODB_USER = os.environ.get('TESTENV_MONGODB_USER')
    TESTENV_MONGODB_PWD = os.environ.get('TESTENV_MONGODB_PWD')
    CONFIRM_TEMPLATE_ID = os.environ.get('CONFIRM_TEMPLATE_ID')
    RESET_TEMPLATE_ID = os.environ.get('RESET_TEMPLATE_ID')
    FRONTEND_BASE_URL = os.environ.get('FRONTEND_BASE_URL')

    DEBUG = True
    MONGODB_SETTINGS = {
        'db': 'progeto-dev',
        'host': '139.59.15.105',
        'username': TESTENV_MONGODB_USER,
        'password': TESTENV_MONGODB_PWD,
        'authentication_source': 'admin'
    }


class TestingConfig(Config):
    TESTENV_MONGODB_USER = os.environ.get('TESTENV_MONGODB_USER')
    TESTENV_MONGODB_PWD = os.environ.get('TESTENV_MONGODB_PWD')
    CONFIRM_TEMPLATE_ID = os.environ.get('CONFIRM_TEMPLATE_ID')
    RESET_TEMPLATE_ID = os.environ.get('RESET_TEMPLATE_ID')
    FRONTEND_BASE_URL = os.environ.get('FRONTEND_BASE_URL')

    TESTING = True
    MONGODB_SETTINGS = {
        'db': 'progeto-dev',
        'host': '10.139.48.99',
        'username': TESTENV_MONGODB_USER,
        'password': TESTENV_MONGODB_PWD,
        'authentication_source': 'admin'
    }


class ProductionConfig(Config):
    TESTENV_MONGODB_USER = os.environ.get('TESTENV_MONGODB_USER')
    TESTENV_MONGODB_PWD = os.environ.get('TESTENV_MONGODB_PWD')
    CONFIRM_TEMPLATE_ID = os.environ.get('CONFIRM_TEMPLATE_ID')
    RESET_TEMPLATE_ID = os.environ.get('RESET_TEMPLATE_ID')
    FRONTEND_BASE_URL = os.environ.get('FRONTEND_BASE_URL')

    MONGODB_SETTINGS = {
        'db': 'progeto-dev',
        'host': '139.59.15.105',
        'username': TESTENV_MONGODB_USER,
        'password': TESTENV_MONGODB_PWD,
        'authentication_source': 'admin'
    }


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': ProductionConfig
}
