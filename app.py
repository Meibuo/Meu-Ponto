from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "chave-secreta-teste")

# 🔹 Configuração do banco PostgreSQL (Render)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://usuario:senha@host:porta/dbname"
)
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

# 🔹 Rotas
@app.route("/")
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def fazer_login():
    email = request.form.get("email")
    senha = request.form.get("senha")

    usuario = Usuario.query.filter_by(email=email).first()
    if usuario and check_password_hash(usuario.senha, senha):
        session["usuario_id"] = usuario.id
        session["usuario_nome"] = usuario.nome
        return redirect(url_for("dashboard"))
    flash("E-mail ou senha incorretos.", "erro")
    return redirect(url_for("login"))

@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

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

@app.route("/dashboard")
def dashboard():
    if "usuario_id" not in session:
        flash("Você precisa estar logado para acessar o dashboard.", "erro")
        return redirect(url_for("login"))
    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da conta.", "sucesso")
    return redirect(url_for("login"))

# 🔹 Execução do app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
