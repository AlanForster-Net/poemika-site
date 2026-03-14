from data import db_session
from data.all_models import User, Jobs
import flask
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from forms.forms import LoginForm


app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "yandex_secret_key"
log = open("logs.txt", mode="+a")

@app.route('/')
def index():
    db_session.global_init("./db/mars_explorer.sqlite")
    db = db_session.create_session()
    j = db.query(Jobs).order_by(Jobs.id).all()
    u = db.query(User).order_by(User.id).all()
    return flask.render_template("worklog.html", jobs=j, users=u)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = LoginForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return flask.redirect("/error/unsame-passwords")
        db_session.global_init("./db/mars_explorer.sqlite")
        db = db_session.create_session()
        if db.query(User).filter(User.email == form.login_email.data).first():
            return flask.redirect("/error/existing-user")
        user = User()
        user.address = form.address.data
        user.age = form.age.data
        user.email = form.login_email.data
        user.name = form.name.data
        user.surname = form.surname.data
        user.position = form.position.data
        user.speciality = form.speciality.data
        user.hashed_password = generate_password_hash(form.password.data)
        db.add(user)
        db.commit()
        return flask.redirect("/success")
    return flask.render_template("loginform.html", form=form, message="")


@app.route("/success")
def success():
    return flask.render_template("success.html")

@app.route("/error/<err>")
def error(err):
    return flask.render_template("error.html", err_code=err)


def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()