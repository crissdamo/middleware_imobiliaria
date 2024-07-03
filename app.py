import os
import logging

from flask import Flask, jsonify
from flask_cors import CORS
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv

from extensions.database import db
from blocklist import BLOCKLIST


from resources.imobiliaria import blp as ImobiliariaBlueprint
from resources.imovel import blp as ImovelBlueprint
from resources.usuario import blp as UsuarioBlueprint


def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Midware API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/docs/"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["API_SPEC_OPTIONS"] = {
        "components": {
            "securitySchemes": {
                "Bearer Auth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "Authorization",
                    "bearerFormat": "JWT",
                    "description": "Enter: **'Bearer &lt;JWT&gt;'**, where JWT is the access token",
                }
            }
        },
    }



    db.init_app(app)
    CORS(app)

    migrate = Migrate(app, db)

    api = Api(app)
    app.config["JWT_SECRET_KEY"] = db_url or os.getenv("JWT_SECRET_KEY")
    jwt = JWTManager(app)




    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        
        return (
            jsonify(
                {
                    "code": 401,
                    "status": "Unauthorized",
                    "message": "Token inválido",
                }
            ),
            401,
        )
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "code": 401,
                    "status": "Unauthorized",
                    "message": "Token prcisa ser atualizado",
                }
            ),
            401,
        )

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "code": 401,
                    "status": "Unauthorized",
                    "message": "Token expirou. ",
                }
            ),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                                {
                    "code": 401,
                    "status": "Unauthorized",
                    "message": "Falha na verificação da assinatura.",
                }
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "code": 401,
                    "status": "Unauthorized",
                    "message": "A solicitação não contém um token de acesso. ",
                }
            ),
            401,
        )
    



    api.register_blueprint(ImobiliariaBlueprint)
    api.register_blueprint(ImovelBlueprint)
    api.register_blueprint(UsuarioBlueprint)

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