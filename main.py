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
        db.add(poem)
        db.commit()
        return flask.redirect("/poems")
    return flask.render_template("createpoem.html", form=form, user=current_user)


@app.route("/poems")
def poems():
    poems = db.query(Poem).all()
    return flask.render_template("poems.html", poems=poems[::-1], user=current_user)


@app.route("/poem/<poem_id>")
def poem(poem_id):
    poem = db.query(Poem).filter(Poem.id == poem_id).first()
    title = poem.title
    body = poem.body.split('#')
    return flask.render_template("poem.html", title=title, body=body, poem=poem)


@app.route("/poem/delete/<poem_id>")
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
    poem = db.query(Poem).filter(Poem.id == poem_id, Poem.author == current_user).first()
    if poem:
        if form.validate_on_submit():
            if form.body.data.strip():
                poem.body = form.body.data.replace('\n', '#')
            if form.title.data.strip():
                poem.title = form.title.data
            return flask.redirect('/poems')
        body = poem.body.split('#')
        db.commit()
        return flask.render_template("updatepoem.html", form=form, user=current_user, poem=poem, body=body)

        


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