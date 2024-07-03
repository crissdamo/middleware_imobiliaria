from marshmallow import Schema, fields, validate

from models.enums.tipo_imovel import TipoImovelEnum


class PlainImobiliariaSchema(Schema):
    id = fields.Int(dump_only=True)
    nome_fantasia = fields.Str(required=True)
    razao_social = fields.Str(allow_none=True)
    cnpj = fields.Str(required=True)
    telefone = fields.Str(required=True)
    email = fields.Str(required=True)


class PlainImovelSchema(Schema):
    id = fields.Int(dump_only=True)
    aluguel = fields.Bool(missing=True)
    venda = fields.Bool(missing=True)
    tipo = fields.Str(validate=validate.OneOf(
        [s.value for s in TipoImovelEnum]))
    ativo = fields.Bool(missing=True)
    valor_venda = fields.Float()
    valor_aluguel = fields.Float()
    rua = fields.Str(required=True)
    numero = fields.Str(required=True)
    bairro = fields.Str(required=True)
    cep = fields.Str(required=True)
    cidade = fields.Str(required=True)
    estado = fields.Str(required=True)
    imobiliaria_id = fields.Int(required=True)
    

class ImobiliariaSchema(PlainImobiliariaSchema):
    imoveis = fields.List(fields.Nested(PlainImovelSchema))


class ImovelSchema(PlainImovelSchema):
    imobiliaria = fields.Nested(PlainImobiliariaSchema)



class PlainUsuarioLoginSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Str(required=True)
    senha = fields.Str(required=True, load_only=True)

class PlainTokenSchema(Schema):
    access_token = fields.Str()
    refresh_token = fields.Str()

class UsuarioTokenSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Str(required=True)
    imobiliaria = fields.Nested(PlainImobiliariaSchema)
    token = fields.Nested(PlainTokenSchema)
