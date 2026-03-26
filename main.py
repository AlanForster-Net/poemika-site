from data import db_session
from data.all_models import User, Poem
import flask
import datetime
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


@app.route('/')
def index():
    return flask.render_template("index.html", user=current_user)


@app.route("/signup", methods=["GET", "POST"])
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


@app.route("/signin", methods=["GET", "POST"])
def signin():
    form = SignInForm()
    if form.validate_on_submit():
        user = db.query(User).filter(User.email == form.email.data).first()
        if user and check_password_hash(user.hashed_password, form.password.data):
            login_user(user, remember=form.remember.data)
            return flask.redirect("/")
        return flask.redirect("/error/bad-user")
    return flask.render_template("signin.html", form=form)


@app.route("/signout")
@login_required
def signout():
    logout_user()
    return flask.redirect("/")

@app.route("/poem/create", methods=["GET", "POST"])
def create_poem():
    form = CreatePoemForm()
    if form.validate_on_submit():
        poem = Poem()
        poem.title = form.title.data
        poem.body = form.body.data.replace('\n', '#')
        poem.author = current_user
        poem.is_private = form.is_private.data
        db.add(poem)
        db.commit()
        return flask.redirect("/poems")
    return flask.render_template("createpoem.html", form=form, user=current_user)


@app.route("/poems")
def poems():
    poems = db.query(Poem).all()
    return flask.render_template("poems.html", poems=poems[::-1], user=current_user)


@app.route("/poem/read/<poem_id>")
def readpoem(poem_id):
    poem = db.get(Poem, poem_id)
    if poem:
        poem.read_count += 1
        db.commit()
        return flask.redirect(f"/poem/{poem_id}")
    return flask.redirect("/error/404")


@app.route("/poem/<poem_id>")
def poem(poem_id):
    poem = db.query(Poem).filter(Poem.id == poem_id).first()
    title = poem.title
    body = poem.body.split('#')
    return flask.render_template("poem.html", title=title, body=body, poem=poem)


@app.route("/poem/delete/<poem_id>")
@login_required
def deletepoem(poem_id):
    poem = db.query(Poem).filter(Poem.id == poem_id).first()
    if not poem:
        return flask.redirect("/error/unexisting")
    author = poem.author
    if current_user == author:
        db.delete(poem)
        db.commit()
    return flask.redirect("/poems")


@app.route("/poem/update/<poem_id>", methods=["GET", "POST"])
@login_required
def updatepoem(poem_id):
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

        
@app.route("/authors")
def authors():
    users = db.query(User).order_by(User.login).all()
    return flask.render_template("authors.html", users=users)

@app.route("/success")
def success():
    return flask.render_template("success.html")


@app.route("/error/<err>")
def error(err):
    return flask.render_template("error.html", err_code=err)


def main():
    app.run(debug=True)

if __name__ == "__main__":
    db_session.global_init("./db/poemikadb.sqlite")
    db = db_session.create_session()
    main()