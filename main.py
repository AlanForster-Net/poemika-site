from data import db_session
from data.all_models import User, Poem
import flask
import datetime
from os.path import abspath
from werkzeug.security import generate_password_hash, check_password_hash
from forms.forms import RegisterForm, SignInForm, CreatePoemForm, UpdatePoemForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user


app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "poemikakey"
login = LoginManager(app)
db = None
log = open("logs.txt", "w")


@login.user_loader
def load_user(user_id):
    return db.get(User, user_id)

# INDEX
@app.route('/')
def index():
    return flask.render_template("index.html", user=current_user)
#INDEX


# USER LOGGING
userlogin = flask.Blueprint("userlogin", __name__, template_folder='/templates')


@userlogin.route("/signup", methods=["GET", "POST"])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return flask.redirect("/error/unsame-passwords")
        if db.query(User).filter(User.email == form.email.data).first():
            return flask.redirect("/error/existing-user")
        user = User()
        user.description = form.description.data
        user.login = form.login.data
        user.email = form.email.data
        user.name = form.name.data
        user.hashed_password = generate_password_hash(form.password.data)
        db.add(user)
        db.commit()
        login_user(user, remember=True)
        return flask.redirect("/")
    return flask.render_template("signup.html", form=form, message="")


@userlogin.route("/signin", methods=["GET", "POST"])
def signin():
    form = SignInForm()
    if form.validate_on_submit():
        user = db.query(User).filter(User.email == form.email.data).first()
        if user and check_password_hash(user.hashed_password, form.password.data):
            login_user(user, remember=form.remember.data)
            return flask.redirect("/")
        return flask.redirect("/error/bad-user")
    return flask.render_template("signin.html", form=form)


@userlogin.route("/signout")
@login_required
def signout():
    logout_user()
    return flask.redirect("/")
# USER LOGGING


# POEM ACTIONS
poem_actions = flask.Blueprint("poemactions", __name__, template_folder='/templates')


@poem_actions.route("/poems")
def poems():
    poems = db.query(Poem).all()
    return flask.render_template("poems.html", poems=poems[::-1], user=current_user)


@poem_actions.route("/poem/read/<poem_id>")
def readpoem(poem_id):
    poem = db.get(Poem, poem_id)
    if poem:
        poem.read_count += 1
        db.commit()
        return flask.redirect(f"/poem/{poem_id}")
    return flask.redirect("/error/404")


@poem_actions.route("/poem/<poem_id>")
def poem(poem_id):
    poem = db.query(Poem).filter(Poem.id == poem_id).first()
    title = poem.title
    body = poem.body.split('#')
    return flask.render_template("poem.html", title=title, body=body, poem=poem)


@poem_actions.route("/poem/create", methods=["GET", "POST"])
def poemCreate():
    form = CreatePoemForm()
    if form.validate_on_submit():
        poem = Poem()
        poem.title = form.title.data
        poem.body = form.body.data.replace('\n', '#')
        poem.author = current_user
        poem.is_private = form.is_private.data
        file = form.file.data
        if file:
            file = abspath(file)
            poem.body = '#'.join(open(file).readlines())
        db.add(poem)
        db.commit()
        return flask.redirect("/poems")
    return flask.render_template("createpoem.html", form=form, user=current_user)


@poem_actions.route("/poem/delete/<poem_id>")
@login_required
def poemDelete(poem_id):
    poem = db.query(Poem).filter(Poem.id == poem_id).first()
    if not poem:
        return flask.redirect("/error/unexisting")
    author = poem.author
    if current_user == author:
        db.delete(poem)
        db.commit()
    return flask.redirect("/poems")


@poem_actions.route("/poem/update/<poem_id>", methods=["GET", "POST"])
@login_required
def poemUpdate(poem_id):
    form = UpdatePoemForm()
    poem = db.get(Poem, poem_id)
    if poem:
        body = poem.body.split('#')
        if form.validate_on_submit():
            poem.title = form.title.data
            poem.body = form.body.data.replace('\n', '#') if not form.left.data else poem.body
            poem.author = current_user
            poem.is_private = form.is_private.data
            db.commit()
            return flask.redirect('/poems')
        return flask.render_template("updatepoem.html", form=form, user=current_user, poem=poem, body=body)
    else:
        return flask.redirect("/error/404")
# POEM ACTIONS


# AUTHOR ACTIONS
author_actions = flask.Blueprint("auhtoractions", __name__, template_folder='/templates')


@author_actions.route("/authors")
def authors():
    users = db.query(User).order_by(User.login).all()
    return flask.render_template("authors.html", users=users)


@author_actions.route("/authors/<author_id>")
def author(author_id):
    author = db.get(User, author_id)
    if author:
        poems = db.query(Poem).filter(Poem.author == author).all()
        return flask.render_template("author.html", author=author, poems=poems)

# TODO реализовать страницу изменения аккаунта
@author_actions.route("/authors/update/<author_id>")
@login_required
def authorUpdate(author_id):
    return "СТОП! Пустая страница", 404
# AUTHOR ACTONS


# REST ACTIONS
api = flask.Blueprint("api", __name__, template_folder='templates')

@api.route("/api/poems", methods=["GET"])
def getPoems():
    return flask.jsonify({
        "poems": [poem.to_dict(only=("id", "author_id", "title", "body", "read_count", "is_private", "created")) for poem in db.query(Poem).all()]
    })


@api.route("/api/poems/<poem_id>", methods=["GET"])
def getPoemById(poem_id):
    poem = db.get(Poem, poem_id)
    if poem:
        return flask.jsonify({
            "poems": poem.to_dict(only=("id", "author_id", "title", "body", "read_count", "is_private", "created"))
        })
    return flask.make_response(flask.jsonify({"code": 404, "reason": "unexisting poem"}))


@api.route("/api/poems", methods=["POST"])
def postPoem():
    if not flask.request.json:
        return flask.make_response(flask.jsonify({"code": 500, "reason": "empty request"}))
    elif not all(header in flask.request.json for header in ("title", "body", "author_id", "password", "is_private")):
        return flask.make_response(flask.jsonify({"code": 500, "reason": "bad request"}))
    poem = Poem()
    req = flask.request.json
    author = db.get(User, req["author_id"])
    if not author or not check_password_hash(author.hashed_password, req["password"]):
        return flask.make_response(flask.jsonify({"code": 403, "reason": "forbidden"}))
    poem.title = req["title"]
    poem.body = req["body"].replace("\n", "#")
    poem.author_id = req["author_id"]
    poem.is_private = req["is_private"]
    db.add(poem)
    db.commit()
    return flask.jsonify({
        "poems": poem.to_dict(only=("id", "author_id", "title", "body", "read_count", "is_private", "created"))
    })


@api.route("/api/poems", methods=["DELETE"])
def deletePoem():
    if not flask.request.json:
        return flask.make_response(flask.jsonify({"code": 500, "reason": "empty request"}))
    elif not all(header in flask.request.json for header in ("id", "password")):
        return flask.make_response(flask.jsonify({"code": 500, "reason": "bad request"}))
    req = flask.request.json
    poem = db.get(Poem, req["id"])
    if not poem:
        return flask.make_response(flask.jsonify({"code": 404, "reason": "unexisting poem"}))
    author = db.get(User, poem.author_id)
    if not check_password_hash(author.hashed_password, req["password"]):
        return flask.make_response(flask.jsonify({"code": 403, "reason": "forbidden"}))
    db.delete(poem)
    db.commit()
    return flask.make_response(flask.jsonify({"code": 200, "reason": "Success delete"}))


@api.route("/api/authors", methods=["GET"])
def getAuthors():
    return flask.jsonify({
        "authors": [author.to_dict(only=("id", "login", "name", "email", "description", "hashed_password")) for author in db.query(User).all()]
    })


@api.route("/api/authors/<author_id>", methods=["GET"])
def getAuthorById(author_id):
    author = db.get(User, author_id)
    if not author:
        return flask.make_response(flask.jsonify({"code": 404, "reason": "unexisting author"}))
    return flask.jsonify({
        "authors": author.to_dict(only=("id", "login", "name", "email", "description", "hashed_password"))
    })


@api.route("/api/authors", methods=["POST"])
def postAuthor():
    if not flask.request.json:
        return flask.make_response(flask.jsonify({"code": 500, "reason": "empty request"}))
    elif not all(header in flask.request.json for header in ("login", "email", "password")):
        return flask.make_response(flask.jsonify({"code": 500, "reason": "bad request"}))
    author = User()
    req = flask.request.json
    author.login = req["login"]
    author.email = req["email"]
    author.hashed_password = generate_password_hash(req["password"])
    if "name" in req:
        author.name = req["name"]
    if "description" in req:
        author.description = req["description"]
    db.add(author)
    db.commit()
    return flask.jsonify({
        "authors": author.to_dict(only=("id", "login", "name", "email", "description", "hashed_password"))
    })

@api.route("/api/authors", methods=["DELETE"])
def deleteAuthor():
    if not flask.request.json:
        return flask.make_response(flask.jsonify({"code": 500, "reason": "empty request"}))
    elif not all(header in flask.request.json for header in ("id", "password")):
        return flask.make_response(flask.jsonify({"code": 500, "reason": "bad request"}))
    req = flask.request.json
    author = db.get(User, req["id"])
    if not author:
        return flask.make_response(flask.jsonify({"code": 404, "reason": "unexisting author"}))
    if not check_password_hash(author.hashed_password, req["password"]):
        return flask.make_response(flask.jsonify({"code": 403, "reason": "forbidden"}))
    db.delete(author)
    db.commit()
    return flask.make_response(flask.jsonify({"code": 200, "reason": "Success delete"}))
# REST ACTIONS


# SYSTEM
system = flask.Blueprint("systempages", __name__, template_folder='/templates')
@system.route("/success")
def success():
    return flask.render_template("success.html")


@system.route("/error/<err>")
def error(err):
    return flask.render_template("error.html", err_code=err)


@system.route("/rules")
def rules():
    return flask.render_template("rules.html")
# SYSTEM

def main():
    app.register_blueprint(api)
    app.register_blueprint(system)
    app.register_blueprint(userlogin)
    app.register_blueprint(poem_actions)
    app.register_blueprint(author_actions)
    app.run(port=5000, debug=True)

if __name__ == "__main__":
    db_session.global_init("./db/poemikadb.sqlite")
    db = db_session.create_session()
    main()