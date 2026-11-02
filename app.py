from flask import Flask
from models import db
from routes import bp as routes_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eficom.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Chave secreta para as mensagens de erro (flash)
app.config['SECRET_KEY'] = 'uma_chave_secreta_super_segura_para_o_mvp'

db.init_app(app)

# Registra as rotas do arquivo routes.py
app.register_blueprint(routes_bp)

@app.route("/")
def inicio():
    return "EFICON — Sistema de Gestão Contábil"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)