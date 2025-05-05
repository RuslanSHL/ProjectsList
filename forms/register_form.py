from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    mail = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Подтвердите пароль', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    info = TextAreaField('Информация о себе')
    github = StringField('Ссылка на свой github')
    image = StringField('Картинка')
    submit = SubmitField('Зарегистрироваться')

