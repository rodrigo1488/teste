from flask import Flask, redirect, url_for
from services import services_bp
from users import users_bp
from clientes import clientes_bp
from relatorios import relatorios_bp
from agenda import agenda_bp
from login import login_bp
import os

app = Flask(__name__)

# Definindo a chave secreta para uso de sessões
app.secret_key = os.urandom(24)

# Registrando os Blueprints
app.register_blueprint(services_bp)
app.register_blueprint(users_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(relatorios_bp)
app.register_blueprint(agenda_bp)
app.register_blueprint(login_bp)

@app.route("/")
def inicio():
    return redirect(url_for('login.login'))  # Redireciona para a página de login

if __name__ == '__main__':
    # Quando rodando em produção, a aplicação vai escutar no IP público e porta definida pela plataforma
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))  # Configuração para plataformas de hospedagem
