import re
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify, Blueprint, render_template, request, redirect, url_for, flash, current_app, get_flashed_messages, send_from_directory
from flask_login import login_user, logout_user, login_required
from models import db, ObrigacaoAcessoria, Cliente, Documento, Usuario
from regras import classificar_obrigacao

bp = Blueprint("main", __name__)

@bp.route("/painel")
@login_required
def painel():
    obrigacoes = ObrigacaoAcessoria.query.all()
    dados = []
    
    total_atrasadas = 0
    total_vence_breve = 0
    total_concluidas = 0
    total_pendentes = 0

    for o in obrigacoes:
        cliente = Cliente.query.get(o.cliente_id)
        status_calculado = classificar_obrigacao(o.data_vencimento, o.status)
        
        if status_calculado == "Atrasada":
            total_atrasadas += 1
        elif status_calculado.startswith("Vence"):
            total_vence_breve += 1
        elif status_calculado == "Concluída":
            total_concluidas += 1
        elif status_calculado == "Pendente":
            total_pendentes += 1

        dados.append({
            "id": o.id, 
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
                           pendentes=total_pendentes)

@bp.route("/clientes")
@login_required
def listar_clientes():
    clientes = Cliente.query.all()
    return render_template("clientes.html", clientes=clientes)

@bp.route("/clientes/importar", methods=["GET", "POST"])
@login_required
def importar_clientes():
    if request.method == "POST":
        arquivo = request.files.get("arquivo_txt")
        
        if not arquivo or not arquivo.filename.endswith('.txt'):
            flash("Por favor, envie um arquivo de texto (.txt) válido.", "erro")
            return redirect(url_for("main.importar_clientes"))

        conteudo = arquivo.read().decode("utf-8")
        linhas = conteudo.splitlines()
        
        nome_atual = None
        cpf_atual = None
        regime_atual = None
        status_atual = None
        
        socio_atual = None
        cpf_socio_atual = None
        ie_atual = None
        icms_atual = None
        
        adicionados = 0
        atualizados = 0
        
        for linha in linhas:
            linha = linha.strip()
            
            if linha.startswith("Nome:"):
                nome_atual = linha.replace("Nome:", "").strip()
            elif linha.startswith("CPF/CNPJ:"):
                cpf_atual = linha.replace("CPF/CNPJ:", "").strip()
            elif linha.startswith("Regime:"):
                regime_atual = linha.replace("Regime:", "").strip()
            elif linha.startswith("Sócio:"):
                socio_atual = linha.replace("Sócio:", "").strip()
            elif linha.startswith("CPF do Sócio:"):
                cpf_socio_atual = linha.replace("CPF do Sócio:", "").strip()
            elif linha.startswith("Inscrição Estadual:"):
                ie_atual = linha.replace("Inscrição Estadual:", "").strip()
            elif linha.startswith("ICMS:"):
                icms_atual = linha.replace("ICMS:", "").strip()
            elif linha.startswith("Status:"):
                status_texto = linha.replace("Status:", "").strip().lower()
                status_atual = True if status_texto == "ativo" else False
                
                if nome_atual and cpf_atual and regime_atual:
                    cliente_existente = Cliente.query.filter_by(cpf_cnpj=cpf_atual).first()
                    
                    if not cliente_existente:
                        novo_cliente = Cliente(
                            nome=nome_atual,
                            cpf_cnpj=cpf_atual,
                            regime_tributario=regime_atual,
                            ativo=status_atual,
                            socio=socio_atual,
                            cpf_socio=cpf_socio_atual,
                            inscricao_estadual=ie_atual,
                            icms=icms_atual
                        )
                        db.session.add(novo_cliente)
                        adicionados += 1
                    else:
                        cliente_existente.nome = nome_atual
                        cliente_existente.regime_tributario = regime_atual
                        cliente_existente.ativo = status_atual
                        cliente_existente.socio = socio_atual
                        cliente_existente.cpf_socio = cpf_socio_atual
                        cliente_existente.inscricao_estadual = ie_atual
                        cliente_existente.icms = icms_atual
                        atualizados += 1
                        
                    nome_atual, cpf_atual, regime_atual, status_atual = None, None, None, None
                    socio_atual, cpf_socio_atual, ie_atual, icms_atual = None, None, None, None
                
        db.session.commit()
        flash(f"Importação concluída! {adicionados} novos adicionados, {atualizados} atualizados.", "sucesso")
        return redirect(url_for("main.listar_clientes"))

    return render_template("importar_clientes.html")

@bp.route("/obrigacoes/nova", methods=["GET", "POST"])
@login_required
def nova_obrigacao():
    if request.method == "POST":
        cliente_id = request.form.get("cliente_id")
        tipo = request.form.get("tipo")
        competencia = request.form.get("competencia")
        vencimento_str = request.form.get("vencimento")
        
        if not cliente_id or not tipo or not competencia or not vencimento_str:
            flash("Por favor, preencha todos os campos.", "erro")
            return redirect(url_for("main.nova_obrigacao"))
            
        try:
            data_vencimento = datetime.strptime(vencimento_str, "%Y-%m-%d").date()
            
            nova_obrigacao = ObrigacaoAcessoria(
                cliente_id=cliente_id,
                tipo_obrigacao=tipo,
                competencia=competencia,
                data_vencimento=data_vencimento,
                status="Pendente"
            )
            
            db.session.add(nova_obrigacao)
            db.session.commit()
            
            flash("Obrigação cadastrada com sucesso!", "sucesso")
            return redirect(url_for("main.painel"))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao cadastrar obrigação: {str(e)}", "erro")
            return redirect(url_for("main.nova_obrigacao"))

    clientes = Cliente.query.filter_by(ativo=True).all()
    return render_template("cadastro_obrigacao.html", clientes=clientes)

@bp.route("/documentos/upload", methods=["GET", "POST"])
@login_required
def upload_documento():
    if request.method == "POST":
        cliente_id = request.form.get("cliente_id")
        tipo_doc = request.form.get("tipo_doc")
        arquivo = request.files.get("arquivo")
        
        if not cliente_id or not tipo_doc or not arquivo or arquivo.filename == '':
            flash("Por favor, preencha todos os campos e selecione um arquivo.", "erro")
            return redirect(url_for("main.upload_documento"))

        filename = secure_filename(arquivo.filename)
        caminho_completo = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        arquivo.save(caminho_completo)
        
        novo_documento = Documento(
            cliente_id=cliente_id,
            nome_arquivo=filename,
            tipo_documento=tipo_doc,
            caminho_armazenamento=caminho_completo,
            status_conferencia="Recebido"
        )
        db.session.add(novo_documento)
        db.session.commit()
        
        flash(f"Documento '{filename}' enviado com sucesso!", "sucesso")
        return redirect(url_for("main.upload_documento"))

    clientes = Cliente.query.filter_by(ativo=True).all()
    return render_template("upload_documento.html", clientes=clientes)

@bp.route("/documentos/enviados")
@login_required
def documentos_enviados():
    documentos = Documento.query.order_by(Documento.id.desc()).all()
    
    dados = []
    for d in documentos:
        cliente = Cliente.query.get(d.cliente_id)
        dados.append({
            "id": d.id,
            "cliente": cliente.nome if cliente else "—",
            "nome_arquivo": d.nome_arquivo,
            "tipo_documento": d.tipo_documento,
            "status": d.status_conferencia
        })
        
    return render_template("documentos_enviados.html", documentos=dados)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
        
        if Usuario.query.count() == 0:
            novo_usuario = Usuario(
                email="gestora@eficom.com.br", 
                senha_hash=generate_password_hash("123456")
            )
            db.session.add(novo_usuario)
            db.session.commit()

        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and check_password_hash(usuario.senha_hash, senha):
            login_user(usuario)
            return redirect(url_for("main.painel"))
        else:
            flash("Usuário ou senha inválidos. Verifique os dados e tente novamente.", "erro")
            
    # Limpa o buffer de mensagens para a tela de login não exibir mensagens antigas
    if request.method == "GET":
        get_flashed_messages(with_categories=True)
            
    return render_template("login.html")

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu do sistema.", "sucesso")
    return redirect(url_for("main.login"))

@bp.route("/clientes/excluir/<int:id>", methods=["POST"])
@login_required
def excluir_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    
    ObrigacaoAcessoria.query.filter_by(cliente_id=cliente.id).delete()
    
    db.session.delete(cliente)
    db.session.commit()
    
    flash(f"Cliente '{cliente.nome}' e seus registros vinculados foram excluídos com sucesso.", "sucesso")
    return redirect(url_for("main.listar_clientes"))

@bp.route("/obrigacoes/atualizar-status/<int:id>", methods=["POST"])
@login_required
def atualizar_status(id):
    obrigacao = ObrigacaoAcessoria.query.get_or_404(id)
    dados = request.get_json()
    novo_status = dados.get("status")
    
    if novo_status in ["Pendente", "Concluída"]:
        obrigacao.status = novo_status
        db.session.commit()
        return jsonify({"sucesso": True, "mensagem": "Status atualizado!"})
        
    return jsonify({"sucesso": False, "mensagem": "Status inválido."}), 400

@bp.route("/obrigacoes/excluir/<int:id>", methods=["POST"])
@login_required
def excluir_obrigacao(id):
    obrigacao = ObrigacaoAcessoria.query.get_or_404(id)
    
    db.session.delete(obrigacao)
    db.session.commit()
    
    flash("Obrigação acessória excluída com sucesso.", "sucesso")
    return redirect(url_for("main.painel"))

@bp.route("/documentos/limpar-todos", methods=["POST"])
@login_required
def limpar_documentos():
    documentos = Documento.query.all()
    
    for doc in documentos:
        if os.path.exists(doc.caminho_armazenamento):
            try:
                os.remove(doc.caminho_armazenamento)
            except Exception:
                pass 
                
        db.session.delete(doc)
        
    db.session.commit()
    
    flash("Todos os documentos recebidos foram apagados com sucesso.", "sucesso")
    return redirect(url_for("main.documentos_enviados"))

@bp.route("/documentos/download/<int:id>")
@login_required
def download_documento(id):
    documento = Documento.query.get_or_404(id)
    
    # current_app.config['UPLOAD_FOLDER'] é a pasta onde os arquivos estão salvos
    # documento.nome_arquivo é o nome do arquivo que a gestora enviou
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'], 
        documento.nome_arquivo, 
        as_attachment=True # Força o navegador a baixar o arquivo
    )
        
    