from flask import Flask

app = Flask(__name__)

@app.route("/")
def inicio():
    return "EFICON — Sistema de Gestão Contábil"

if __name__ == "__main__":
    app.run(debug=True)