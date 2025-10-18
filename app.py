from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Conexão com PostgreSQL - coloque sua URL aqui
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://meuponto:f62wXQtozjw2Mielya41xlfpqXu4YCZS@dpg-d3ps91u3jp1c7386vg8g-a/meuponto'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)

# Criar tabelas
with app.app_context():
    db.create_all()

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario_form = request.form['usuario']
        senha_form = request.form['senha']

        user = Usuario.query.filter_by(usuario=usuario_form).first()
        if user and check_password_hash(user.senha, senha_form):
            session['usuario'] = user.usuario
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha incorretos!', 'error')

    return render_template('login.html')

# Rota de cadastro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuario_form = request.form['usuario']
        senha_form = request.form['senha']

        # Verifica se usuário já existe
        if Usuario.query.filter_by(usuario=usuario_form).first():
            flash('Usuário já existe!', 'error')
            return redirect(url_for('register'))

        # Cria usuário com senha hash
        novo_usuario = Usuario(
            usuario=usuario_form,
            senha=generate_password_hash(senha_form)
        )
        db.session.add(novo_usuario)
        db.session.commit()

        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Dashboard simples
@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return f"Bem-vindo {session['usuario']}! Você está logado."

# Logout
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
