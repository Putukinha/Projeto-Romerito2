from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_login import login_user, logout_user
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["SECRET_KEY"] = "lojagames123"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lojagames.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin, db.Model):

    __tablename__ = "usuarios"

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    
    nome = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    senha = db.Column(
        db.String(255),
        nullable=False
    )

class Game(db.Model):

    __tablename__ = "games"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(120),
        nullable=False
    )

    plataforma = db.Column(
        db.String(80),
        nullable=False
    )

    preco = db.Column(
        db.Float,
        nullable=False
    )

    estoque = db.Column(
        db.Integer,
        nullable=False
    )

class Venda(db.Model):

    __tablename__ = "vendas"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    game_id = db.Column(
        db.Integer,
        db.ForeignKey("games.id"),
        nullable=False
    )

    quantidade = db.Column(
        db.Integer,
        nullable=False
    )

    data = db.Column(
        db.String(20),
        nullable=False
    )

    game = db.relationship("Game")

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    if request.method == "POST":

        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        usuario = User.query.filter_by(email=email).first()

        if usuario:
            return render_template(
                "cadastro.html",
                erro="Este e-mail já está cadastrado."
            )

        senha_hash = generate_password_hash(senha)

        novo_usuario = User(
            nome=nome,
            email=email,
            senha=senha_hash
        )

        db.session.add(novo_usuario)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("cadastro.html")



@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":

        email = request.form["email"]
        senha = request.form["senha"]

        usuario = User.query.filter_by(email=email).first()

        if usuario:

            if check_password_hash(usuario.senha, senha):

                login_user(usuario)

                return redirect(url_for("index"))

        return render_template(
            "login.html",
            erro="E-mail ou senha incorretos."
        )

    return render_template("login.html")