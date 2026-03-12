from .db_session import SqlAlchemyBase
import datetime
import sqlalchemy
import sqlalchemy.orm as orm


class User(SqlAlchemyBase):
    __tablename__ = "users"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    surname = sqlalchemy.Column(sqlalchemy.String)
    name = sqlalchemy.Column(sqlalchemy.String)
    age = sqlalchemy.Column(sqlalchemy.Integer)
    position = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    speciality = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    job = orm.relationship("Jobs", back_populates="user")

    def __repr__(self):
        return f"<Colonist> {self.id} {self.surname} {self.name}"


class Jobs(SqlAlchemyBase):
    __tablename__ = "jobs"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    team_leader = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    job = sqlalchemy.Column(sqlalchemy.String)
    work_size = sqlalchemy.Column(sqlalchemy.Integer)
    collaborators = sqlalchemy.Column(sqlalchemy.String)
    start_date = sqlalchemy.Column(sqlalchemy.DateTime)
    end_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean)
    user = orm.relationship("User")

    def getData(self):
        return (self.id, self.job, self.team_leader, self.work_size, self.colaborators, self.is_finished)