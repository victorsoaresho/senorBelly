from flask import Flask, jsonify

from controllers.user_controller import user_bp
from controllers.debt_controller import debt_bp
from controllers.receivable_controller import receivable_bp

app = Flask(__name__)

app.register_blueprint(user_bp)
app.register_blueprint(debt_bp)
app.register_blueprint(receivable_bp)


@app.route("/")
def home():
    """
    Rota inicial de teste da API.
    
    Retorna uma mensagem de boas-vindas para confirmar que a API está rodando.
    """
    return jsonify({"message": "Bem-vindo à API do SenorBelly!"})


if __name__ == "__main__":
    app.run(debug=True, port=3000)
