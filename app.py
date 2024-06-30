
import os
import models
from flask import Flask, logging
from flask_cors import CORS
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint
from dotenv import load_dotenv
import logging.handlers
from extensions.database import db


def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False



    
    db.init_app(app)
    CORS(app)
    migrate = Migrate(app, db)








    # SWAGGER: configuração da documentação Swagger

    SWAGGER_URL = '/docs'
    API_URL = '/static/swagger.json'
    SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Middleware Integração"
        }
    )
    app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)




    @app.get("/hello_world")
    def hello_world():
        return "<p>Hello, World!</p>"



    # LOGFILE: configuração do arquivo d elog

    LOGFILE = 'middleware.log'   #Log-File-Name
    LOGFILESIZE = 5000000    #Log-File-Size (bytes)
    LOGFILECOUNT = 4 #Rotate-Count-File

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    h = logging.handlers.RotatingFileHandler(LOGFILE, maxBytes=LOGFILESIZE, backupCount=LOGFILECOUNT)
    f = logging.Formatter('[%(asctime)s] %(levelname)s:%(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    h.setFormatter(f)
    logger.addHandler(h)
    logging.info('api started')


    return app