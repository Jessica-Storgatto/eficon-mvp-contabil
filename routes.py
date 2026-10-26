from flask import Blueprint, render_template
from models import ObrigacaoAcessoria, Cliente
from regras import classificar_obrigacao

bp = Blueprint("main", __name__)

@bp.route("/painel")
def painel():
    obrigacoes = ObrigacaoAcessoria.query.all()
    dados = []
    for o in obrigacoes:
        cliente = Cliente.query.get(o.cliente_id)
        dados.append({
            "cliente": cliente.nome if cliente else "—",
            "tipo": o.tipo_obrigacao,
            "competencia": o.competencia,
            "vencimento": o.data_vencimento.strftime("%d/%m/%Y"),
            "status": classificar_obrigacao(o.data_vencimento, o.status),
        })
    return render_template("painel.html", obrigacoes=dados)