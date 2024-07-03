import logging.handlers
from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models.imobiliaria import ImobiliariaModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from extensions.database import db
from models.imovel import ImovelModel
from schema import ImovelSchema, PlainImovelSchema, PlainImovelSchema
from security import jwt_required_with_doc


blp = Blueprint("Imovel", "imovel", description="Operações sobre imovel")


@blp.route("/imovel")
class Imovel(MethodView):

    @jwt_required_with_doc()
    @blp.arguments(PlainImovelSchema)
    @blp.response(201, ImovelSchema)
    def post(self, imovel_data):
        """
        Cria um novo imóvel.

        **Descrição:** Recebe os dados de um novo imóvel, valida e persiste no banco de dados.
        Se ocorrer um erro durante a operação de banco de dados, retorna um erro 400 ou 500.

        **Parâmetros:**
            imovel_data (dict): Os dados do imóvel a ser criado.

        **Retorna:**
            Um objeto JSON com as informações do imóvel criado.
        """

        # Dados recebidos:
        
        aluguel = imovel_data['aluguel']
        venda = imovel_data.get('venda')
        tipo = imovel_data.get('tipo')
        ativo = imovel_data.get('ativo')
        valor_venda = imovel_data.get('valor_venda')
        valor_aluguel = imovel_data.get('valor_aluguel')
        rua = imovel_data.get('rua')
        numero = imovel_data.get('numero')
        bairro = imovel_data.get('bairro')
        cep = imovel_data.get('cep')
        cidade = imovel_data.get('cidade')
        estado = imovel_data.get('estado')
        imobiliaria_id = imovel_data.get('imobiliaria_id')


        imobiliaria = ImobiliariaModel().query.get_or_404(imobiliaria_id)
        # Cria objeto:

        imovel = ImovelModel(
            aluguel=aluguel,
            venda=venda,
            tipo=tipo,
            ativo=ativo,
            valor_venda=valor_venda,
            valor_aluguel=valor_aluguel,
            rua=rua,
            numero=numero,
            bairro=bairro,
            cep=cep,
            cidade=cidade,
            estado=estado,
            imobiliaria=imobiliaria,
        )

       
        # Salva em BD
        try:
            db.session.add(imovel)
            db.session.commit()
            message = f"Imóvel criada com sucesso"
            logging.debug(message)
    
        except IntegrityError as error:
            message = f"400: Error ao criar imovel: {error}"
            logging.warning(message)
            abort(
                400,
                message="Erro ao criar imovel.",
            )
        except SQLAlchemyError as error:
            message = f"500: Error ao criar imovel: {error}"
            logging.warning(message)
            abort(500, message="Server Error.")


        imovel_schema = ImovelSchema()
        result = imovel_schema.dump(imovel)

        return jsonify(result)
    
    @jwt_required_with_doc()
    @blp.response(200, ImovelSchema)
    def get(self,):
        """
        Lista todos os imóveis.

        **Descrição:** Busca e retorna todos os imóveis cadastrados no banco de dados.
        Se ocorrer um erro durante a operação de banco de dados, retorna um erro 500.

        **Retorna:**
            Uma lista de objetos JSON com as informações dos imóveis.
        """
        result_lista = []
        imoveis = ImovelModel().query.all()

        for imovel in imoveis:
            imovel_schema = ImovelSchema()
            result = imovel_schema.dump(imovel)
            result_lista.append(result)

        return jsonify(result_lista)
    
    
@blp.route("/imovel/<int:id>")
class ImovelID(MethodView):

    @jwt_required_with_doc()
    @blp.arguments(PlainImovelSchema)
    @blp.response(201, ImovelSchema)
    def put(self, imovel_data, id):
        """
        Atualiza um imóvel existente.

        **Descrição:** Recebe os dados de um imóvel existente e atualiza suas informações no banco de dados.
        Se ocorrer um erro durante a operação de banco de dados, retorna um erro 400 ou 500.

        **Parâmetros:**
            imovel_data (dict): Os dados do imóvel a ser atualizado.
            id (int): O ID do imóvel a ser atualizado.

        **Retorna:**
            Um objeto JSON com as informações do imóvel atualizado.
        """

        imovel = ImovelModel().query.get_or_404(id)

        # Dados recebidos:
        aluguel = imovel_data['aluguel']
        venda = imovel_data.get('venda')
        tipo = imovel_data.get('tipo')
        ativo = imovel_data.get('ativo')
        valor_venda = imovel_data.get('valor_venda')
        valor_aluguel = imovel_data.get('valor_aluguel')
        rua = imovel_data.get('rua')
        numero = imovel_data.get('numero')
        bairro = imovel_data.get('bairro')
        cep = imovel_data.get('cep')
        cidade = imovel_data.get('cidade')
        estado = imovel_data.get('estado')



        # Cria objeto:
    
        imovel.aluguel=aluguel
        imovel.venda=venda
        imovel.tipo=tipo
        imovel.ativo=ativo
        imovel.valor_venda=valor_venda
        imovel.valor_aluguel=valor_aluguel
        imovel.rua=rua
        imovel.numero=numero
        imovel.bairro=bairro
        imovel.cep=cep
        imovel.cidade=cidade
        imovel.estado=estado
        

        # Salva em BD
        try:
            db.session.add(imovel)
            db.session.commit()
            message = f"Imóvel editado com sucesso"
            logging.debug(message)
    
        except IntegrityError as error:
            message = f"400: Error ao editar imovel: {error}"
            logging.warning(message)
            abort(
                400,
                message="Erro ao editar imóvel.",
            )
        except SQLAlchemyError as error:
            message = f"500: Error ao editar imovel: {error}"
            logging.warning(message)
            abort(500, message="Server Error.")


        imovel_schema = ImovelSchema()
        result = imovel_schema.dump(imovel)

        return jsonify(result)
    
    @jwt_required_with_doc()
    @blp.response(200, ImovelSchema)
    def get(self, id):
        """
        Busca um imóvel pelo seu ID.

        **Descrição:** Busca o imóvel pelo ID e retorna suas informações.
        Se ocorrer um erro durante a operação de banco de dados, retorna um erro 404 ou 500.

        **Parâmetros:**
            id (int): O ID do imóvel a ser buscado.

        **Retorna:**
            Um objeto JSON com as informações do imóvel.
        """
        imovel = ImovelModel().query.get_or_404(id)
        imovel_schema = ImovelSchema()
        result = imovel_schema.dump(imovel)
        return jsonify(result)
    
    @jwt_required_with_doc()
    def delete(self, id):
        """
            Deleta um imóvel pelo seu ID.

            **Descrição:** Remove o imóvel com o ID especificado do banco de dados.
            Se ocorrer um erro durante a operação de banco de dados, retorna um erro 400 ou 500.

            **Parâmetros:**
                id (int): O ID do imóvel a ser deletado.

            **Retorna:**
                Um objeto JSON com uma mensagem de confirmação.
        """
        
        
        try:
            imovel = ImovelModel().query.get_or_404(id)
            db.session.delete(imovel)
            db.session.commit()
            message = f"Imóvel excluído com sucesso"
            logging.debug(message)
    
        except IntegrityError as error:
            message = f"Error delete imovel: {error}"
            logging.warning(message)
            abort(
                400,
                message="Erro ao deletar empresa."
            )
        except SQLAlchemyError as error:
            message = f"Error delete empresa: {error}"
            logging.warning(message)
            abort(500, message="Server Error.")

        context = {"message": message}

        return jsonify(context)
    