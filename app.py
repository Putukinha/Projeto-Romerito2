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



@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("login"))


@app.route("/games")
@login_required
def games():

    pesquisa = request.args.get("pesquisa", "")

    if pesquisa:
        lista_games = Game.query.filter(
            Game.nome.contains(pesquisa)
        ).all()
    else:
        lista_games = Game.query.all()

    return render_template(
        "games.html",
        games=lista_games,
        pesquisa=pesquisa
    )



@app.route("/games/novo", methods=["GET", "POST"])
@login_required
def novo_game():

    if request.method == "POST":

        nome = request.form["nome"]
        plataforma = request.form["plataforma"]
        preco = float(request.form["preco"])
        estoque = int(request.form["estoque"])

        game = Game(
            nome=nome,
            plataforma=plataforma,
            preco=preco,
            estoque=estoque
        )

        db.session.add(game)
        db.session.commit()

        return redirect(url_for("games"))

    return render_template("novo_game.html")


@app.route("/games/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_game(id):

    game = Game.query.get_or_404(id)

    if request.method == "POST":

        game.nome = request.form["nome"]
        game.plataforma = request.form["plataforma"]
        game.preco = float(request.form["preco"])
        game.estoque = int(request.form["estoque"])

        db.session.commit()

        return redirect(url_for("games"))

    return render_template(
        "editar_game.html",
        game=game
    )


@app.route("/games/excluir/<int:id>")
@login_required
def excluir_game(id):

    game = Game.query.get_or_404(id)

    db.session.delete(game)
    db.session.commit()

    return redirect(url_for("games"))


@app.route("/vendas")
@login_required
def vendas():

    lista_vendas = Venda.query.all()

    return render_template(
        "vendas.html",
        vendas=lista_vendas
    )


@app.route("/vendas/nova", methods=["GET", "POST"])
@login_required
def nova_venda():

    games = Game.query.all()

    if request.method == "POST":

        game_id = int(request.form["game"])
        quantidade = int(request.form["quantidade"])
        data = request.form["data"]

        game = Game.query.get(game_id)

        if game.estoque < quantidade:

            return render_template(
                "nova_venda.html",
                games=games,
                erro="Estoque insuficiente."
            )

        venda = Venda(
            game_id=game_id,
            quantidade=quantidade,
            data=data
        )

        game.estoque -= quantidade

        db.session.add(venda)
        db.session.commit()

        return redirect(url_for("vendas"))

    return render_template(
        "nova_venda.html",
        games=games
    )



@app.route("/vendas/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_venda(id):

    venda = Venda.query.get_or_404(id)
    games = Game.query.all()

    if request.method == "POST":

        venda.game_id = int(request.form["game"])
        venda.quantidade = int(request.form["quantidade"])
        venda.data = request.form["data"]

        db.session.commit()

        return redirect(url_for("vendas"))

    return render_template(
        "editar_venda.html",
        venda=venda,
        games=games
    )



@app.route("/vendas/excluir/<int:id>")
@login_required
def excluir_venda(id):

    venda = Venda.query.get_or_404(id)

    game = Game.query.get(venda.game_id)

    game.estoque += venda.quantidade

    db.session.delete(venda)
    db.session.commit()

    return redirect(url_for("vendas"))


if __name__ == "__main__":
    app.run(debug=True)
