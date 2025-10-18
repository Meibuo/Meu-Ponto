from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'SUA_CHAVE_SECRETA'

# Configuração do banco de dados PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://meuponto:f62wXQtozjw2Mielya41xlfpqXu4YCZS@dpg-d3ps91u3jp1c7386vg8g-a/meuponto'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de Usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)

# Rota de login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email, senha=senha).first()
        if usuario:
            session['usuario_id'] = usuario.id
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou senha incorretos!')
    return render_template('login.html')

# Rota de cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado!')
            return redirect(url_for('cadastro'))
        novo_usuario = Usuario(nome=nome, email=email, senha=senha)
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Cadastro realizado com sucesso!')
        return redirect(url_for('login'))
    return render_template('cadastro.html')

# Rota do dashboard
@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    return "Bem-vindo ao Dashboard!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
