from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'sua_chave_secreta_aqui')

# URL do banco do Render ou local
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql+psycopg://meuponto:f62wXQtozjw2Mielya41xlfpqXu4YCZS@dpg-d3ps91u3jp1c7386vg8g-a/meuponto'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de Usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)

# Cria tabelas se não existirem
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        user = Usuario.query.filter_by(usuario=usuario).first()
        if not user or not check_password_hash(user.senha, senha):
            flash('Usuário ou senha incorretos.', 'danger')
            return redirect(url_for('login'))

        session['usuario'] = user.usuario
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        if Usuario.query.filter_by(usuario=usuario).first():
            flash('Usuário já existe.', 'warning')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(senha, method='sha256')
        novo_usuario = Usuario(usuario=usuario, senha=hashed_password)
        db.session.add(novo_usuario)
        db.session.commit()

        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        flash('Faça login primeiro.', 'warning')
        return redirect(url_for('login'))
    return f"Bem-vindo, {session['usuario']}! <a href='/logout'>Sair</a>"

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash('Logout realizado.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
