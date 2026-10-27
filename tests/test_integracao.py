import pytest
from app import app
from models import db, Cliente, ObrigacaoAcessoria
from datetime import date, timedelta

@pytest.fixture
def client():
    # Em vez de configurar o banco de novo, apenas limpamos o banco que já existe no app
    with app.app_context():
        db.drop_all()   # Limpa qualquer sujeira de testes anteriores
        db.create_all() # Cria as tabelas novamente
        
        with app.test_client() as client:
            yield client
        
        db.session.remove()
        db.drop_all()

def test_criar_obrigacao_no_banco(client):
    with app.app_context():
        novo_cliente = Cliente(nome="Cliente Teste", cpf_cnpj="123", regime_tributario="MEI")
        db.session.add(novo_cliente)
        db.session.commit()
        
        nova_obrigacao = ObrigacaoAcessoria(
            cliente_id=novo_cliente.id, 
            tipo_obrigacao="DCTF", 
            competencia="10/2026", 
            data_vencimento=date.today() + timedelta(days=5)
        )
        db.session.add(nova_obrigacao)
        db.session.commit()
        
        obrigacao_salva = ObrigacaoAcessoria.query.first()
        assert obrigacao_salva is not None
        assert obrigacao_salva.tipo_obrigacao == "DCTF"
        assert obrigacao_salva.cliente.nome == "Cliente Teste"