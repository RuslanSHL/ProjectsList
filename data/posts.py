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
    like = sa.Column(sa.Integer, default=0)
    dislike = sa.Column(sa.Integer, default=0)
    create_time = sa.Column(sa.DateTime, default=datetime.now)

    author = sa.orm.relationship('User', back_populates='posts')
    author_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))

    users_who_liked = sa.orm.relationship('User', back_populates='liked_posts', secondary='rating_posts')

    comments = sa.orm.relationship('Comment', back_populates='post')


class RatingPosts(SqlAlchemyBase):
    __tablename__ = 'rating_posts'

    post_id = sa.Column(sa.Integer, sa.ForeignKey('posts.id'), primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), primary_key=True)
    rating = sa.Column(sa.Integer)

