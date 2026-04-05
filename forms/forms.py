from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, EmailField, SubmitField, TextAreaField, BooleanField, FileField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    login = StringField("Кто вы среди поэтов?", validators=[DataRequired()])
    name = StringField("Каково Ваше настоящее имя?", default="Неизвестный")
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
    file = FileField("Загрузить файл", default="")
    is_private = BooleanField("Хотите сделать приватным?")
    submit = SubmitField("Записать")


class UpdatePoemForm(FlaskForm):
    title = StringField("Название", validators=[DataRequired()])
    body = TextAreaField("Текст")
    left = BooleanField("Оставить текст прежним?")
    is_private = BooleanField("Хотите сделать приватным?")
    submit = SubmitField("Записать")