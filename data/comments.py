import sqlalchemy as sa
from datetime import datetime
from .db_session import SqlAlchemyBase


class Comment(SqlAlchemyBase):
    __tablename__ = 'comments'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    text = sa.Column(sa.String)
    like = sa.Column(sa.Integer)
    dislike = sa.Column(sa.Integer)
    create_time = sa.Column(sa.DateTime, default=datetime.now)

    author = sa.orm.relationship('User', back_populates='comments')
    author_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))

    post = sa.orm.relationship('Post', back_populates='comments')
    post_id = sa.Column(sa.Integer, sa.ForeignKey('posts.id'))

    answer_id = sa.Column(sa.Integer, sa.ForeignKey('comments.id'))
