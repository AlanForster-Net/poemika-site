from .db_session import SqlAlchemyBase
import datetime
import sqlalchemy
import sqlalchemy.orm as orm
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = "users"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    login = sqlalchemy.Column(sqlalchemy.String)
    name = sqlalchemy.Column(sqlalchemy.String, default="Неизвестный")
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    description = sqlalchemy.Column(sqlalchemy.Text, default="Я поэт, тем и интересен")
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    poems = orm.relationship("Poem", back_populates="author")
    


class Poem(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "poems"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey(User.id))
    author = orm.relationship("User")
    title = sqlalchemy.Column(sqlalchemy.String(25))
    body = sqlalchemy.Column(sqlalchemy.Text)
    read_count = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    created = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())