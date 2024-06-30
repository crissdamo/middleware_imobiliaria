from extensions.database import db

class ImobiliariaModel(db.Model):
    __tablename__ = "imobiliaria"

    id = db.Column(db.Integer, primary_key=True)
    nome_fantasia = db.Column(db.String, unique=True, nullable=False)
    razao_social = db.Column(db.String, nullable=True)
    cnpj = db.Column(db.String, unique=True, nullable=False)
    telefone = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    
    imoveis = db.relationship("ImovelModel", back_populates="imobiliaria", lazy="dynamic")
