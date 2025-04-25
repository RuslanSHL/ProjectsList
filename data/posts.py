import sqlalchemy as sa
from datetime import datetime
from .db_session import SqlAlchemyBase


class Post(SqlAlchemyBase):
    __tablename__ = 'posts'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title = sa.Column(sa.String)
    text = sa.Column(sa.String)
    project_link = sa.Column(sa.String)
    category = sa.Column(sa.String)
    like = sa.Column(sa.Integer)
    dislike = sa.Column(sa.Integer)
    create_time = sa.Column(sa.DateTime, default=datetime.now)

    author = sa.orm.relationship('User', back_populates='posts')
    author_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))

    comments = sa.orm.relationship('Comment', back_populates='post')
