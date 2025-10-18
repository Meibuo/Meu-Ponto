from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "sua_chave_secreta"  # Troque para algo seguro em produção

# Configuração do banco SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ponto.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)  # senha hashed

# Modelo de registro de ponto
class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    tipo = db.Column(db.String(20))  # "Entrada" ou "Saída"
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Cria o banco de dados dentro do contexto da aplicação
with app.app_context():
    if not os.path.exists('ponto.db'):
        db.create_all()

# Rota raiz
@app.route('/')
def index():
    if 'usuario_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        user = Usuario.query.filter_by(usuario=usuario).first()
        if user and check_password_hash(user.senha, senha):
            session['usuario_id'] = user.id
            session['usuario_nome'] = user.usuario
            flash(f'Bem-vindo, {user.usuario}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha incorretos.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Cadastro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        if Usuario.query.filter_by(usuario=usuario).first():
            flash('Usuário já existe. Escolha outro.', 'warning')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(senha, method='sha256')
        novo_usuario = Usuario(usuario=usuario, senha=hashed_password)
        db.session.add(novo_usuario)
        db.session.commit()

        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'usuario_id' not in session:
        flash('Faça login para acessar o dashboard.', 'warning')
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']
    usuario_nome = session['usuario_nome']
    user = Usuario.query.get(usuario_id)

    if request.method == 'POST':
        tipo = request.form['tipo']  # "Entrada" ou "Saída"
        registro = Registro(usuario_id=user.id, tipo=tipo)
        db.session.add(registro)
        db.session.commit()
        flash(f'{tipo} registrada com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    registros = Registro.query.filter_by(usuario_id=user.id).order_by(Registro.timestamp.desc()).all()
    return render_template('dashboard.html', usuario=user, registros=registros)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu da conta.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
