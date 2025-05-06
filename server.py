import os
os.system('color')

import requests

from data import db_session
from data.users import User
from data.posts import Post
from data.comments import Comment

import flask
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from forms.register_form import RegisterForm
from forms.login_form import LoginForm
from forms.post_form import PostForm
from forms.comment_form import CommentForm

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'lms_yandex_ru'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db = db_session.create_session()
    return db.query(User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return flask.render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")

        db = db_session.create_session()
        if db.query(User).filter(User.mail == form.mail.data).first():
            return flask.render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такая почта уже зарегестрирована")
        user = User(
            name=form.name.data,
            mail=form.mail.data,
            github=form.github.data,
            info=form.info.data,
            image=form.image.data,
        )
        user.set_password(form.password.data)
        db.add(user)
        db.commit()
        return flask.redirect('/login')
    return flask.render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db = db_session.create_session()
        user = db.query(User).filter(User.mail == form.mail.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            return flask.redirect('/')
        else:
            return flask.render_template('login.html', message='Неправильный логин или пороль', form=form)
    else:
        return flask.render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return flask.redirect("/")


@app.route('/user<int:user_id>')
def user_page(user_id):
    db = db_session.create_session()
    user = db.query(User).filter(User.id == user_id).first()
    return flask.render_template('user_page.html', title='Страница пользователя', user=user)


@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        db = db_session.create_session()
        post = Post(
            title=form.title.data,
            text=form.text.data,
            project_link=form.project_link.data,
            category=form.category.data,
            author_id=current_user.id
        )
        db.add(post)
        db.commit()
        return flask.redirect('/')
    return flask.render_template('add_post.html', title='Новый пост', form=form)


@app.route('/new')
@app.route('/')
def posts_list_new():
    db = db_session.create_session()
    posts = db.query(Post).all()[::-1]
    return flask.render_template('posts_list.html', title='Посты', posts=posts)


@app.route('/<category>')
def posts_list(category):
    db = db_session.create_session()
    posts = db.query(Post).filter(Post.category==category).all()
    return flask.render_template('posts_list.html', title='Посты', posts=posts)


@app.route('/post_like/<int:id>/<action>')
def post_like_action(id, action):
    print(action, id, current_user.id)
    db = db_session.create_session()
    post = db.query(Post).filter(Post.id == id).first()
    if action == 'like':
        post.like += 1
    else:
        post.dislike += 1
    db.commit()
    return flask.redirect(flask.request.referrer)


@app.route('/comment_like/<int:id>/<action>')
def comment_like_action(id, action):
    print(action, id, current_user.id)
    db = db_session.create_session()
    comment = db.query(Comment).filter(Comment.id == id).first()
    if action == 'like':
        comment.like += 1
    else:
        comment.dislike += 1
    db.commit()
    return flask.redirect(flask.request.referrer)


@app.route('/posts/<int:id>', methods=['GET', 'POST'])
def post_view(id):
    form = CommentForm()
    db = db_session.create_session()
    post = db.query(Post).filter(Post.id==id).first()
    if form.validate_on_submit():
        print('GET')
        comment = Comment()
        comment.post_id = post.id
        comment.author_id = current_user.id
        comment.text = form.text.data
        db.add(comment)
        db.commit()
    return flask.render_template('post_view.html', title=post.title, post=post, form=form)


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def post_edit(id):
    db = db_session.create_session()
    post = db.query(Post).filter(Post.id==id).first()
    if current_user.id == post.author_id or current_user.id == 1:
        form = PostForm()
        if not form.validate_on_submit():
            form.title.data = post.title
            form.text.data = post.text
            form.project_link.data = post.project_link
            form.category.data = post.category

            return flask.render_template('add_post.html', title='Изменить пост', form=form)
        else:
            post.title = form.title.data
            post.text = form.text.data
            post.project_link = form.project_link.data
            post.category = form.category.data
            db.commit()
            return flask.redirect(f'/posts/{id}')
    else:
        return 'В доступе запрещено'


if __name__ == '__main__':
    db_session.global_init('db/database.db')
    app.run(port=8080, host='127.0.0.1')
