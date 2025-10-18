from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "minha_chave_secreta"

# Configuração do banco PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://meuponto:f62wXQtozjw2Mielya41xlfpqXu4YCZS@dpg-d3ps91u3jp1c7386vg8g-a/meuponto"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de Usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)

# Rota de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.senha, senha):
            session['user_id'] = usuario.id
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("E-mail ou senha incorretos", "danger")
    return render_template('login.html')

# Rota de Cadastro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = generate_password_hash(request.form['senha'])
        
        # Verifica se o usuário já existe
        if Usuario.query.filter_by(email=email).first():
            flash("E-mail já cadastrado", "danger")
            return redirect(url_for('register'))
        
        novo_usuario = Usuario(nome=nome, email=email, senha=senha)
        db.session.add(novo_usuario)
        db.session.commit()
        
        flash("Cadastro realizado com sucesso!", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

# Rota Dashboard (apenas exemplo)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return f"Bem-vindo! ID do usuário: {session['user_id']}"

# Rota Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logout realizado com sucesso!", "success")
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria tabelas se não existirem
    app.run(debug=True)
