from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "sua_chave_secreta"

# Configuração do banco SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ponto.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)  # senha hashed

# Cria o banco se não existir
if not os.path.exists('ponto.db'):
    db.create_all()

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        user = Usuario.query.filter_by(usuario=usuario).first()
        if user and check_password_hash(user.senha, senha):
            flash(f'Bem-vindo, {usuario}!', 'success')
            return redirect(url_for('dashboard'))  # cria rota dashboard depois
        else:
            flash('Usuário ou senha incorretos.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Rota de cadastro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        if Usuario.query.filter_by(usuario=usuario).first():
            flash('Usuário já existe. Escolha outro.', 'warning')
            return redirect(url_for('register'))

        # Cria hash da senha
        hashed_password = generate_password_hash(senha, method='sha256')

        novo_usuario = Usuario(usuario=usuario, senha=hashed_password)
        db.session.add(novo_usuario)
        db.session.commit()

        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Dashboard (exemplo simples)
@app.route('/dashboard')
def dashboard():
    return "<h1>Bem-vindo ao Meu Ponto!</h1><p>Em breve, aqui você verá seus registros de ponto.</p>"

# Rota raiz redireciona para login
@app.route('/')
def index():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
