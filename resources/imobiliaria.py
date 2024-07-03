import logging.handlers
from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from extensions.database import db
from models.imobiliaria import ImobiliariaModel

from schema import ImobiliariaSchema, PlainImobiliariaSchema
from security import jwt_required_with_doc
from utilities.apenas_digitos import apenas_digitos
from utilities.valida_cnpj import validar_cnpj
from utilities.valida_email import validar_email
from utilities.valida_telefone import validar_telefone

blp = Blueprint("Imobiliaria", "imobiliaria", description="Operações sobre imobiliária")


@blp.route("/imobiliaria")
class Imobiliaria(MethodView):

    @jwt_required_with_doc()
    @blp.arguments(PlainImobiliariaSchema)
    @blp.response(201, ImobiliariaSchema)
    def post(self, imobiliaria_data):
        """
        Cria uma nova imobiliária.

        **Descrição:** Recebe os dados de uma nova imobiliária, valida e persiste no banco de dados.
        Se ocorrer um erro durante a operação de banco de dados, retorna um erro 400 ou 500.

        **Parâmetros:**
            imobiliaria_data (dict): Os dados da imobiliária a ser criada.

        **Retorna:**
            Um objeto JSON com as informações da imobiliária criada.
        """

        # Dados recebidos:
        
        nome_fantasia = imobiliaria_data['nome_fantasia']
        razao_social = imobiliaria_data.get('razao_social')
        cnpj = imobiliaria_data.get('cnpj')
        telefone = imobiliaria_data.get('telefone')
        email = imobiliaria_data.get('email')


        # validações:

        if ImobiliariaModel.query.filter(ImobiliariaModel.email == email).first():
            message="E-mail já cadastrado"
            logging.error(message)
            abort(409, message=message)

        if not validar_email(email):
            message="E-mail inválido"
            logging.error(message)
            abort(409, message=message)
        
        if ImobiliariaModel.query.filter(ImobiliariaModel.cnpj == cnpj).first():
            message="CNPJ já cadastrado"
            logging.error(message)
            abort(409, message=message)

        if not validar_cnpj(cnpj):
            message="CNPJ inválido"
            logging.error(message)
            abort(409, message=message)
        
        if not validar_telefone(telefone):
            message="Formato do telefone inválido"
            logging.error(message)
            abort(409, message=message)
        
        cnpj = apenas_digitos(str(cnpj))
        telefone = apenas_digitos(str(telefone))



        # Cria objeto:

        imobiliaria = ImobiliariaModel(
            nome_fantasia=nome_fantasia,
            razao_social=razao_social,
            cnpj=cnpj,
            telefone=telefone,
            email=email,
        )

       
        # Salva em BD
        try:
            db.session.add(imobiliaria)
            db.session.commit()
            message = f"Imobiliária criada com sucesso"
            logging.debug(message)
    
        except IntegrityError as error:
            message = f"400: Error ao criar imobiliaria: {error}"
            logging.warning(message)
            abort(
                400,
                message="Erro ao criar imobiliária.",
            )
        except SQLAlchemyError as error:
            message = f"500: Error ao criar imobiliaria: {error}"
            logging.warning(message)
            abort(500, message="Server Error.")


        imobiliaria_schema = ImobiliariaSchema()
        result = imobiliaria_schema.dump(imobiliaria)

        return jsonify(result)
    
    @jwt_required_with_doc()
    @blp.response(200, ImobiliariaSchema)
    def get(self,):
        """
            Lista todas as imobiliárias.

            **Descrição:** Busca e retorna todas as imobiliárias cadastradas no banco de dados.
            Se ocorrer um erro durante a operação de banco de dados, retorna um erro 500.

            **Retorna:**
                Uma lista de objetos JSON com as informações das imobiliárias.
        """

        result_lista = []
        imobiliarias = ImobiliariaModel().query.all()

        for imobiliaria in imobiliarias:
            imobiliaria_schema = ImobiliariaSchema()
            result = imobiliaria_schema.dump(imobiliaria)
            result_lista.append(result)

        return jsonify(result_lista)
    
    
@blp.route("/imobiliaria/<int:id>")
class ImobiliariaID(MethodView):

    @jwt_required_with_doc()
    @blp.arguments(PlainImobiliariaSchema)
    @blp.response(201, ImobiliariaSchema)
    def put(self, imobiliaria_data, id):
        """
        Atualiza uma imobiliária existente.

        **Descrição:** Recebe os dados de uma imobiliária existente e atualiza suas informações no banco de dados.
        Se ocorrer um erro durante a operação de banco de dados, retorna um erro 400 ou 500.

        **Parâmetros:**
            imobiliaria_data (dict): Os dados da imobiliária a ser atualizada.
            id (int): O ID da imobiliária a ser atualizada.

        **Retorna:**
            Um objeto JSON com as informações da imobiliária atualizada.
        """

        imobiliaria = ImobiliariaModel().query.get_or_404(id)

        # Dados recebidos:
        nome_fantasia = imobiliaria_data['nome_fantasia']
        razao_social = imobiliaria_data.get('razao_social')
        cnpj = imobiliaria_data.get('cnpj')
        telefone = imobiliaria_data.get('telefone')
        email = imobiliaria_data.get('email')


        # validações:

        if imobiliaria.email != email:
            if ImobiliariaModel.query.filter(ImobiliariaModel.email == email).first():
                message="E-mail já cadastrado"
                logging.error(message)
                abort(409, message=message)

        if not validar_email(email):
            message="E-mail inválido"
            logging.error(message)
            abort(409, message=message)
        
        if imobiliaria.cnpj != cnpj:
            if ImobiliariaModel.query.filter(ImobiliariaModel.cnpj == cnpj).first():
                message="CNPJ já cadastrado"
                logging.error(message)
                abort(409, message=message)

        if not validar_cnpj(cnpj):
            message="CNPJ inválido"
            logging.error(message)
            abort(409, message=message)
        
        if not validar_telefone(telefone):
            message="Formato do telefone inválido"
            logging.error(message)
            abort(409, message=message)
        
        cnpj = apenas_digitos(str(cnpj))
        telefone = apenas_digitos(str(telefone))



        # Cria objeto:

    
        imobiliaria.nome_fantasia=nome_fantasia
        imobiliaria.razao_social=razao_social
        imobiliaria.cnpj=cnpj
        imobiliaria.telefone=telefone
        imobiliaria.email=email
        

        # Salva em BD
        try:
            db.session.add(imobiliaria)
            db.session.commit()
            message = f"Imobiliária editada com sucesso"
            logging.debug(message)
    
        except IntegrityError as error:
            message = f"400: Error ao editar imobiliaria: {error}"
            logging.warning(message)
            abort(
                400,
                message="Erro ao editar imobiliária.",
            )
        except SQLAlchemyError as error:
            message = f"500: Error ao editar imobiliaria: {error}"
            logging.warning(message)
            abort(500, message="Server Error.")


        imobiliaria_schema = ImobiliariaSchema()
        result = imobiliaria_schema.dump(imobiliaria)

        return jsonify(result)
    
    @jwt_required_with_doc()
    @blp.response(200, ImobiliariaSchema)
    def get(self, id):
        """
            Busca uma imobiliária pelo seu ID.

            **Descrição:** Busca a imobiliária pelo ID e retorna suas informações.
            Se ocorrer um erro durante a operação de banco de dados, retorna um erro 404 ou 500.

            **Parâmetros:**
                id (int): O ID da imobiliária a ser buscada.

            **Retorna:**
                Um objeto JSON com as informações da imobiliária.
        """
        imobiliaria = ImobiliariaModel().query.get_or_404(id)
        imobiliaria_schema = ImobiliariaSchema()
        result = imobiliaria_schema.dump(imobiliaria)
        return jsonify(result)
    
    @jwt_required_with_doc()
    def delete(self, id):
        """
        Deleta uma imobiliária pelo seu ID.

        **Descrição:** Remove a imobiliária com o ID especificado do banco de dados.
        Se ocorrer um erro durante a operação de banco de dados, retorna um erro 400 ou 500.

        **Parâmetros:**
            id (int): O ID da imobiliária a ser deletada.

        **Retorna:**
            Um objeto JSON com uma mensagem de confirmação.
        """
        try:
            imobiliaria = ImobiliariaModel().query.get_or_404(id)
            db.session.delete(imobiliaria)
            db.session.commit()
            message = f"Imobiliária excluída com sucesso"
            logging.debug(message)
    
        except IntegrityError as error:
            message = f"Error delete imovel: {error}"
            logging.warning(message)
            abort(
                400,
                message="Erro ao deletar imovel."
            )
        except SQLAlchemyError as error:
            message = f"Error delete imovel: {error}"
            logging.warning(message)
            abort(500, message="Server Error.")

        context = {"message": message}

        return jsonify(context)
    