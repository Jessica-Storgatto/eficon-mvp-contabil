from flask import Blueprint, render_template
from models import ObrigacaoAcessoria, Cliente
from regras import classificar_obrigacao

bp = Blueprint("main", __name__)

@bp.route("/painel")
def painel():
    obrigacoes = ObrigacaoAcessoria.query.all()
    dados = []
    
    # Variáveis para os cartões de resumo
    total_atrasadas = 0
    total_vence_breve = 0
    total_concluidas = 0

    for o in obrigacoes:
        cliente = Cliente.query.get(o.cliente_id)
        status_calculado = classificar_obrigacao(o.data_vencimento, o.status)
        
        # Contabiliza para os cartões
        if status_calculado == "Atrasada":
            total_atrasadas += 1
        elif status_calculado.startswith("Vence"):
            total_vence_breve += 1
        elif status_calculado == "Concluída":
            total_concluidas += 1

        dados.append({
            "cliente": cliente.nome if cliente else "—",
            "tipo": o.tipo_obrigacao,
            "competencia": o.competencia,
            "vencimento": o.data_vencimento.strftime("%d/%m/%Y"),
            "status": status_calculado,
        })
        
    return render_template("painel.html", 
                           obrigacoes=dados, 
                           atrasadas=total_atrasadas,
                           vence_breve=total_vence_breve,
                           concluidas=total_concluidas)

@bp.route("/clientes")
def listar_clientes():
    clientes = Cliente.query.all()
    return render_template("clientes.html", clientes=clientes)

@bp.route("/obrigacoes/nova")
def nova_obrigacao():
    # Busca os clientes cadastrados para preencher o select
    clientes = Cliente.query.filter_by(ativo=True).all()
    return render_template("cadastro_obrigacao.html", clientes=clientes)

@bp.route("/documentos/upload")
def upload_documento():
    clientes = Cliente.query.filter_by(ativo=True).all()
    return render_template("upload_documento.html", clientes=clientes)