from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'minha_chave_secreta')

# URL do banco (Render ou local)
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql+psycopg://meuponto:f62wXQtozjw2Mielya41xlfpqXu4YCZS@dpg-d3ps91u3jp1c7386vg8g-a/meuponto'
)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de usuário
class Usuario(db.Model):
    __tablename__ = 'usuarios'
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
        usuario_form = request.form['usuario']
        senha_form = request.form['senha']

        usuario = Usuario.query.filter_by(usuario=usuario_form).first()
        if not usuario:
            flash('Usuário não encontrado.', 'danger')
            return redirect(url_for('login'))

        if not check_password_hash(usuario.senha, senha_form):
            flash('Senha incorreta.', 'danger')
            return redirect(url_for('login'))

        session['usuario'] = usuario.usuario
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuario_form = request.form['usuario']
        senha_form = request.form['senha']

        if not usuario_form or not senha_form:
            flash('Preencha todos os campos!', 'warning')
            return redirect(url_for('register'))

        if Usuario.query.filter_by(usuario=usuario_form).first():
            flash('Usuário já existe!', 'warning')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(senha_form, method='sha256')
        novo_usuario = Usuario(usuario=usuario_form, senha=hashed_password)
        try:
            db.session.add(novo_usuario)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar: {str(e)}', 'danger')
            return redirect(url_for('register'))

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
