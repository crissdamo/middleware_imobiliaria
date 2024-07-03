from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, get_jwt
import logging.handlers

from blocklist import BLOCKLIST
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from extensions.database import db


from models.usuario import UsuarioModel
from schema import PlainUsuarioLoginSchema, UsuarioTokenSchema
from security import jwt_required_with_doc


blp = Blueprint("Usuários", "usuários", description="Operações sobre o usuário")


@blp.route("/registrar")
class RegistrarUsuario(MethodView):

    @blp.response(200, PlainUsuarioLoginSchema)
    @blp.arguments(PlainUsuarioLoginSchema)
    def post(self, usuario_data):
        """
        Registra um novo usuário.

        **Descrição:** Recebe os dados de um novo usuário, valida e persiste no banco de dados.
        Se o e-mail já estiver cadastrado, retorna um erro 409.
        Se ocorrer um erro durante a operação de banco de dados, retorna um erro 400 ou 500.

        **Parâmetros:**
            usuario_data (dict): Os dados do usuário a ser criado.

        **Retorna:**
            Um objeto JSON com as informações do usuário criado.
        """

        email = usuario_data["email"]
        senha = usuario_data["senha"]

        if UsuarioModel.query.filter(UsuarioModel.email == email).first():
            abort(409, message="E-mail já cadastrado")
        
        usuario = UsuarioModel(
            email=email,
            senha=pbkdf2_sha256.hash(senha),
        )

        # Salva em BD
        try:
            db.session.add(usuario)
            db.session.commit()

            message = f"Usuário criado com sucesso"
            logging.info(message)
    
        except IntegrityError as error:
            message = f"Error create usuario: {error}"
            logging.warning(message)
            abort(
                400,
                message="Erro ao criar usuario.",
            )
        except SQLAlchemyError as error:
            message = f"Error create usuario: {error}"
            logging.warning(message)
            abort(500, message="Server Error.")



        # return {"message": "Usuário criado com sucesso."}, 201

        usuario_schema = PlainUsuarioLoginSchema()
        result = usuario_schema.dump(usuario)
      
        return jsonify(result)


@blp.route("/login")
class UsuarioLogin(MethodView):

    @blp.arguments(PlainUsuarioLoginSchema)
    @blp.response(200, UsuarioTokenSchema)
    def post(self, usuario_data):
        """
        Realiza login de um usuário.

        **Descrição:** Recebe as credenciais do usuário, valida e gera tokens de acesso e atualização.
        Se as credenciais forem inválidas, retorna um erro 401.

        **Parâmetros:**
            usuario_data (dict): As credenciais do usuário (e-mail e senha).

        **Retorna:**
            Um objeto JSON com as informações do usuário e os tokens de acesso e atualização.
        """

        email = usuario_data["email"]
        senha = usuario_data["senha"]
    
        usuario = UsuarioModel.query.filter(
            UsuarioModel.email == email
        ).first()

        if usuario and pbkdf2_sha256.verify(senha, usuario.senha):

           
            # usuario = UsuarioModel.query.filter(UsuarioModel.imobiliaria == usuario).first()
            if usuario:
                usuario_id = usuario.id
            
                dados_usuario = {
                    "usuario_id": usuario_id
                }

                access_token = create_access_token(
                    identity=usuario.id, 
                    additional_claims=dados_usuario, 
                    fresh=True
                )
                refresh_token = create_refresh_token(identity=usuario.id)


                usuario_schema = UsuarioTokenSchema()
                result = usuario_schema.dump(usuario)
                result["token"] = {"access_token": access_token, "refresh_token": refresh_token}

                
                return jsonify(result)
        
        abort(401, message="Credenciais inválidas.")


@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required_with_doc(refresh=True)
    def post(self):
        """
            Gera um novo token de acesso usando um token de atualização.

            **Descrição:** Gera um novo token de acesso a partir de um token de atualização válido.
            Se ocorrer um erro durante a operação, retorna um erro 401.

            **Retorna:**
                Um objeto JSON com o novo token de acesso.
        """

        usuario_atual = get_jwt_identity()
        novo_token = create_access_token(identity=usuario_atual, fresh=False)
        return {"access_token": novo_token}


@blp.route("/logout")
class usuarioLogout(MethodView):
        
    @jwt_required_with_doc()
    def post(self):
        """
        Realiza o logout do usuário.

        **Descrição:** Invalida o token de acesso atual, adicionando-o a uma lista de bloqueio.
        Se ocorrer um erro durante a operação, retorna um erro 401.

        **Retorna:**
            Um objeto JSON com uma mensagem de confirmação de logout.
        """

        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Logout realizado com sucesso."}
