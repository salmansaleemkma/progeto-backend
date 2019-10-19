from flask import Flask
from config import config
from flask_moment import Moment
from flask_mongoengine import MongoEngine
from flask_cors import CORS
import os

moment = Moment()
db = MongoEngine()

def create_app(config_name):

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    moment.init_app(app)
    db.init_app(app)
    
    if config_name == 'development' or config_name == 'testing':
        cors = CORS()
        print('CORS initiated for '+config_name+' environment')
        cors.init_app(app)

    from .adminboard import adminboard as adminboard_blueprint
    app.register_blueprint(adminboard_blueprint, url_prefix='/progeto-admin')

    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

    return app
