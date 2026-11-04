import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, ObrigacaoAcessoria, Cliente
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
    total_pendentes = 0 # <-- NOVA VARIÁVEL AQUI

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
        elif status_calculado == "Pendente": # <-- NOVA VERIFICAÇÃO AQUI
            total_pendentes += 1

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
                           concluidas=total_concluidas,
                           pendentes=total_pendentes) # <-- ENVIANDO PARA O HTML
        
    return render_template("painel.html", 
                           obrigacoes=dados, 
                           atrasadas=total_atrasadas,
                           vence_breve=total_vence_breve,
                           concluidas=total_concluidas)

@bp.route("/clientes")
def listar_clientes():
    clientes = Cliente.query.all()
    return render_template("clientes.html", clientes=clientes)

@bp.route("/clientes/importar", methods=["GET", "POST"])
def importar_clientes():
    if request.method == "POST":
        arquivo = request.files.get("arquivo_txt")
        
        if not arquivo or not arquivo.filename.endswith('.txt'):
            flash("Por favor, envie um arquivo de texto (.txt) válido.", "erro")
            return redirect(url_for("main.importar_clientes"))

        # Lê o conteúdo do arquivo e separa em linhas
        conteudo = arquivo.read().decode("utf-8")
        linhas = conteudo.splitlines()
        
        # Variáveis para montar o cliente temporário
        nome_atual = None
        cpf_atual = None
        regime_atual = None
        status_atual = None
        
        adicionados = 0
        atualizados = 0
        
        for linha in linhas:
            linha = linha.strip() # Remove espaços em branco e o famoso \r do Windows
            
            if linha.startswith("Nome:"):
                nome_atual = linha.replace("Nome:", "").strip()
            elif linha.startswith("CPF/CNPJ:"):
                cpf_atual = linha.replace("CPF/CNPJ:", "").strip()
            elif linha.startswith("Regime:"):
                regime_atual = linha.replace("Regime:", "").strip()
            elif linha.startswith("Status:"):
                # Pega o texto do status e limpa
                status_texto = linha.replace("Status:", "").strip().lower()
                status_atual = True if status_texto == "ativo" else False
                
                # Quando chegamos no Status, o bloco do cliente está completo! 
                # Agora sim salvamos no banco.
                if nome_atual and cpf_atual and regime_atual:
                    cliente_existente = Cliente.query.filter_by(cpf_cnpj=cpf_atual).first()
                    
                    if not cliente_existente:
                        novo_cliente = Cliente(
                            nome=nome_atual,
                            cpf_cnpj=cpf_atual,
                            regime_tributario=regime_atual,
                            ativo=status_atual
                        )
                        db.session.add(novo_cliente)
                        adicionados += 1
                    else:
                        cliente_existente.nome = nome_atual
                        cliente_existente.regime_tributario = regime_atual
                        cliente_existente.ativo = status_atual
                        atualizados += 1
                        
                    # Limpa as variáveis para o próximo cliente da lista
                    nome_atual, cpf_atual, regime_atual, status_atual = None, None, None, None
                
        db.session.commit()
        flash(f"Importação concluída! {adicionados} novos adicionados, {atualizados} atualizados.", "sucesso")
        return redirect(url_for("main.listar_clientes"))

    return render_template("importar_clientes.html")

@bp.route("/obrigacoes/nova", methods=["GET", "POST"])
def nova_obrigacao():
    if request.method == "POST":
        # Pega os dados digitados no formulário
        cliente_id = request.form.get("cliente_id")
        tipo = request.form.get("tipo")
        competencia = request.form.get("competencia")
        vencimento_str = request.form.get("vencimento")
        
        # Validação básica de segurança
        if not cliente_id or not tipo or not competencia or not vencimento_str:
            flash("Por favor, preencha todos os campos.", "erro")
            return redirect(url_for("main.nova_obrigacao"))
            
        try:
            # Converte o texto "2026-11-15" (do input date) para objeto de data do Python
            from datetime import datetime
            data_vencimento = datetime.strptime(vencimento_str, "%Y-%m-%d").date()
            
            # Cria a nova obrigação no banco
            nova_obrigacao = ObrigacaoAcessoria(
                cliente_id=cliente_id,
                tipo_obrigacao=tipo,
                competencia=competencia,
                data_vencimento=data_vencimento,
                status="Pendente" # Toda nova obrigação nasce como pendente
            )
            
            db.session.add(nova_obrigacao)
            db.session.commit()
            
            flash("Obrigação cadastrada com sucesso!", "sucesso")
            return redirect(url_for("main.painel")) # Manda de volta pro painel
            
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao cadastrar obrigação: {str(e)}", "erro")
            return redirect(url_for("main.nova_obrigacao"))

    # Se for GET, apenas carrega a tela
    clientes = Cliente.query.filter_by(ativo=True).all()
    return render_template("cadastro_obrigacao.html", clientes=clientes)

@bp.route("/documentos/upload")
def upload_documento():
    clientes = Cliente.query.filter_by(ativo=True).all()
    return render_template("upload_documento.html", clientes=clientes)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
        
        # Validação simples para o MVP (no futuro, usar hash seguro)
        if email == "gestora@eficom.com.br" and senha == "123456":
            return redirect(url_for("main.painel"))
        else:
            flash("Usuário ou senha inválidos. Verifique os dados e tente novamente.", "erro")
            
    return render_template("login.html")

@bp.route("/clientes/excluir/<int:id>", methods=["POST"])
def excluir_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    
    # 1. Apaga todas as obrigações e documentos vinculados a este cliente
    ObrigacaoAcessoria.query.filter_by(cliente_id=cliente.id).delete()
    # Documento.query.filter_by(cliente_id=cliente.id).delete() # Descomente se a tabela Documento estiver sendo usada
    
    # 2. Apaga o cliente
    db.session.delete(cliente)
    db.session.commit()
    
    flash(f"Cliente '{cliente.nome}' e seus registros vinculados foram excluídos com sucesso.", "sucesso")
    return redirect(url_for("main.listar_clientes"))