from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, EmailField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    login = StringField("Кто вы среди поэтов?", validators=[DataRequired()])
    name = StringField("Каково Ваше настоящее имя?")
    email = EmailField("Эл. почта", validators=[DataRequired()])
    password = PasswordField("Придумайте пароль", validators=[DataRequired()])
    password_again = PasswordField("Повторите пароль", validators=[DataRequired()])
    description = TextAreaField("Если хотите, расскажите немного о себе")
    submit = SubmitField("Регистрация")


class SignInForm(FlaskForm):
    email = EmailField("Эл. почта", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember = BooleanField("Запомните меня")
    submit = SubmitField("Войти")


class CreatePoemForm(FlaskForm):
    title = StringField("Название", validators=[DataRequired()])
    body = TextAreaField("Текст", validators=[DataRequired()])
    submit = SubmitField("Создать")


class UpdatePoemForm(FlaskForm):
    title = StringField("Название", default="")
    body = TextAreaField("Текст", default="")
    submit = SubmitField("Изменить")