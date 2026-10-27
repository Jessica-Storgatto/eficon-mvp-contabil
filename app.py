from flask import Flask
from models import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eficom.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route("/")
def inicio():
    return "EFICON — Sistema de Gestão Contábil"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)