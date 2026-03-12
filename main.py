from data import db_session
from data.all_models import User, Jobs
import flask
import datetime


app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "yandex_secret_key"


@app.route('/')
def index():
    db_session.global_init("./db/mars_explorer.sqlite")
    db = db_session.create_session()
    j = db.query(Jobs).order_by(Jobs.id).all()
    u = db.query(User).order_by(User.id).all()
    return flask.render_template("worklog.html", jobs=j, users=u)


def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()