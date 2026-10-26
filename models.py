from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class Cliente(db.Model):
    __tablename__ = "clientes"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    cpf_cnpj = db.Column(db.String(18), nullable=False, unique=True)
    regime_tributario = db.Column(db.String(50), nullable=False)
    ativo = db.Column(db.Boolean, default=True)

class Documento(db.Model):
    __tablename__ = "documentos"
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    tipo_documento = db.Column(db.String(50), nullable=False)
    caminho_armazenamento = db.Column(db.String(500), nullable=False)
    status_conferencia = db.Column(db.String(20), default="Recebido")

class ObrigacaoAcessoria(db.Model):
    __tablename__ = "obrigacoes"
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    tipo_obrigacao = db.Column(db.String(150), nullable=False)
    competencia = db.Column(db.String(7), nullable=False)  # MM/AAAA
    data_vencimento = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default="Pendente")

    def dias_para_vencimento(self):
        return (self.data_vencimento - date.today()).days