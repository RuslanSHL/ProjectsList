from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, SelectField, StringField
from wtforms.validators import DataRequired, Optional


class PostForm(FlaskForm):
    text = TextAreaField('Текст поста')
    title = StringField('Заголовок поста')
    project_link = StringField('Ссылка на проект')
    category = SelectField('Категория поста',
                           choices=['Интересное',
                                    'Хороший код',
                                    'Оптимизированное',
                                    'Красивый дизайн'
                                    ]
                           )
    submit = SubmitField('Опубликовать')
