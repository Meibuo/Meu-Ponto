from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import os
import logging

# Configuração básica do Flask
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "chave-secreta-teste")

# Configuração do banco PostgreSQL (Render)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://usuario:senha@host:porta/banco"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializa o SQLAlchemy
db = SQLAlchemy(app)

# Modelo de usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)

# Cria tabelas se não existirem
with app.app_context():
    db.create_all()

# Configuração de logging
logging.basicConfig(level=logging.INFO)

# Página de login
@app.route("/")
def login():
    return render_template("login.html")

# Página de cadastro
@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

# Endpoint para registrar usuário
@app.route("/registrar", methods=["POST"])
def registrar():
    try:
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")

        # Validação básica
        if not nome or not email or not senha:
            flash("Preencha todos os campos.", "erro")
            return redirect(url_for("cadastro"))

        # Verifica se o email já existe
        if Usuario.query.filter_by(email=email).first():
            flash("E-mail já cadastrado!", "erro")
            return redirect(url_for("cadastro"))

        # Cria usuário com senha criptografada
        senha_hash = generate_password_hash(senha)
        novo_usuario = Usuario(nome=nome, email=email, senha=senha_hash)

        # Tenta adicionar no banco
        db.session.add(novo_usuario)
        db.session.commit()

        flash("Cadastro realizado com sucesso!", "sucesso")
        return redirect(url_for("login"))

    except Exception as e:
        # Faz rollback e loga o erro
        db.session.rollback()
        logging.exception("Erro ao registrar usuário:")
        flash(f"Erro ao cadastrar: {str(e)}", "erro")
        return redirect(url_for("cadastro"))

if __name__ == "__main__":
    # Debug=True apenas para desenvolvimento; não usar em produção
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
