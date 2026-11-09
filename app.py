import os
from flask import Flask
from flask_login import LoginManager
from flask import redirect, url_for
from models import db, Usuario
from routes import bp as routes_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eficom.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Chave secreta para as mensagens de erro (flash)
app.config['SECRET_KEY'] = 'uma_chave_secreta_super_segura_para_o_mvp'

# --- CONFIGURAÇÕES DE UPLOAD ---
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

# --- CONFIGURAÇÃO DO LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login' # Se não estiver logado, manda pra rota 'login'
login_manager.login_message = "Por favor, faça login para acessar o sistema."
login_manager.login_message_category = "erro"

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Registra as rotas do arquivo routes.py
app.register_blueprint(routes_bp)

@app.route("/")
def inicio():
    return redirect(url_for("main.login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
else:
    # Esse bloco roda no Render (produção)
    with app.app_context():
        db.create_all()
        # Cria o usuário padrão se ele não existir
        from models import Usuario
        from werkzeug.security import generate_password_hash
        if Usuario.query.count() == 0:
            admin = Usuario(
                email="gestora@eficom.com.br", 
                senha_hash=generate_password_hash("123456")
            )
            db.session.add(admin)
            db.session.commit()    