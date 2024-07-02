from extensions.database import db
from sqlalchemy import Enum
from models.enums.tipo_imovel import TipoImovelEnum


class ImovelModel(db.Model):
    __tablename__ = "imovel"

    id = db.Column(db.Integer, primary_key=True)
    aluguel = db.Column(db.Boolean, default=True)
    venda = db.Column(db.Boolean, default=True)
    tipo = db.Column(Enum(TipoImovelEnum))
    ativo = db.Column(db.Boolean, default=True)
    valor_venda = db.Column(db.Float)
    valor_aluguel = db.Column(db.Float)
    rua = db.Column(db.String(256), nullable=False)
    numero = db.Column(db.String(10), nullable=False)
    bairro = db.Column(db.String(256), nullable=False)
    cep = db.Column(db.String(10), nullable=False)
    cidade = db.Column(db.String(256), nullable=False)
    estado = db.Column(db.String(256), nullable=False)
    
    imobiliaria_id = db.Column(db.Integer, db.ForeignKey("imobiliaria.id"), unique=False, nullable=False)
    imobiliaria = db.relationship("ImobiliariaModel", back_populates="imoveis")
