from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    uname = StringField("Имя пользователя: ")
    pwd = PasswordField("Пароль :", validators=[DataRequired(), Length(min=4, max=16)])
    remember = BooleanField("Запомнить меня", default=False)
    submit = SubmitField("Войти")

class AddWorks(FlaskForm):
    title = StringField("Название работы ")
    desc = TextAreaField("Описание работы: ")