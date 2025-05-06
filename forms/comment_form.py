from flask_wtf import FlaskForm
from wtforms import  SubmitField, TextAreaField
from wtforms.validators import DataRequired


class CommentForm(FlaskForm):
    text = TextAreaField('Текст комментария', validators=(DataRequired(), ))
    submit = SubmitField('Отправить')


