from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Inicialização do app Flask
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("SECRET_KEY", "chave-secreta-teste")

# 🔹 Configuração do banco PostgreSQL (Render)
db_url = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://meuponto:f62wXQtozjw2Mielya41xlfpqXu4YCZS@dpg-d3ps91u3jp1c7386vg8g-a/meuponto"
)

# Render às vezes envia URL com "postgres://" — precisa trocar pra "postgresql://"
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# 🔹 Modelo de usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

# 🔹 Página inicial
@app.route("/")
def home():
    return redirect(url_for("login"))

# 🔹 Página de login
@app.route("/login")
def login():
    return render_template("login.html")

# 🔹 Página de cadastro
@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

# 🔹 Função para registrar usuário
@app.route("/registrar", methods=["POST"])
def registrar():
    nome = request.form.get("nome")
    email = request.form.get("email")
    senha = request.form.get("senha")

    if not nome or not email or not senha:
        flash("Preencha todos os campos.", "erro")
        return redirect(url_for("cadastro"))

    if Usuario.query.filter_by(email=email).first():
        flash("E-mail já cadastrado!", "erro")
        return redirect(url_for("cadastro"))

    senha_hash = generate_password_hash(senha)
    novo_usuario = Usuario(nome=nome, email=email, senha=senha_hash)
    db.session.add(novo_usuario)
    db.session.commit()

    flash("Cadastro realizado com sucesso!", "sucesso")
    return redirect(url_for("login"))

# 🔹 Teste rápido (opcional)
@app.route("/teste")
def teste():
    return "Servidor rodando normalmente!"

# 🔹 Execução
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
