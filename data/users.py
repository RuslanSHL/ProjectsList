import sqlalchemy as sa
from datetime import datetime
from .db_session import SqlAlchemyBase

from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String)
    mail = sa.Column(sa.String, unique=True)
    hashed_password = sa.Column(sa.String)
    info = sa.Column(sa.String)
    image = sa.Column(sa.String)
    github = sa.Column(sa.String)
    create_time = sa.Column(sa.DateTime, default=datetime.now)

    posts = sa.orm.relationship('Post', back_populates='author')

    comments = sa.orm.relationship('Comment', back_populates='author')

    liked_posts = sa.orm.relationship('Post', back_populates='users_who_liked', secondary='rating_posts')
    liked_comments = sa.orm.relationship('Comment', back_populates='users_who_liked', secondary='rating_comments')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
