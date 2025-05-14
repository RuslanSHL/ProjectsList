import os
os.system('color')

import requests

from PIL import Image
import io

from data import db_session
from data.users import User
from data.posts import Post, RatingPosts
from data.comments import Comment, RatingComments

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


def get_repo_info(github_link: str):
    try:
        if 'github.com' in github_link:
            name, repo = github_link.rstrip('/').split('/')[-2:]
            info = requests.get(f'https://api.github.com/repos/{name}/{repo}').json()
            out = {'stars': info['watchers_count'],
                   'image': info['owner']['avatar_url'],
                    'author': name,
                    'description': info['description'],
                    'language': info['language']}
            return out
        else:
            return {}
    except Exception as e:
        print('Возникла проблема с API', e)
        return {}


@login_manager.user_loader
def load_user(user_id):
    try:
        db = db_session.create_session()
        return db.query(User).get(user_id)
    finally:
        db.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        form = RegisterForm()
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return flask.render_template('register.html', title='Регистрация',
                                    form=form,
                                    message="Пароли не совпадают", edit=False)

            db = db_session.create_session()
            if db.query(User).filter(User.mail == form.mail.data).first():
                db.close()
                return flask.render_template('register.html', title='Регистрация',
                                    form=form,
                                    message="Такая почта уже зарегестрирована", edit=False)
            user = User(
                name=form.name.data,
                mail=form.mail.data,
                github=form.github.data,
                info=form.info.data,
            )
            user.set_password(form.password.data)
            db.add(user)

            f = form.image.data
            if f:
                user.image = f'static/img/img{user.id}.jpg'
                image_stream = io.BytesIO(f.read())
                img = Image.open(image_stream)
                width, height = img.size
                if width > height:
                    delta = (width - height) // 2
                    img = img.crop((delta, 0, width - delta, height))
                else:
                    delta = (height - width) // 2
                    img = img.crop((0, delta, width, height - delta))
                img = img.resize((320, 320))
                img = img.convert('RGB')
                img.save(user.image)
            else:
                user.image = 'static/img/img_standart.jpg'
            db.commit()
            return flask.redirect('/login')
        return flask.render_template('register.html', title='Регистрация', form=form, edit=False)
    finally:
        db.close()


@app.route('/login', methods=['GET', 'POST'])
def login():
        form = LoginForm()
        if form.validate_on_submit():
            try:
                db = db_session.create_session()
                user = db.query(User).filter(User.mail == form.mail.data).first()
                if user and user.check_password(form.password.data):
                    login_user(user, remember=True)
                    return flask.redirect('/')
                else:
                    return flask.render_template('login.html', message='Неправильный логин или пароль', form=form)
            finally:
                db.close()
        else:
            return flask.render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return flask.redirect("/")


@app.route('/user<int:user_id>')
def user_page(user_id):
    try:
        db = db_session.create_session()
        user = db.query(User).filter(User.id == user_id).first()
        return flask.render_template('user_page.html', title='Страница пользователя', user=user)
    finally:
        db.close()


@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
        form = PostForm()
        if form.validate_on_submit():
            try:
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
            finally:
                db.close()
        return flask.render_template('add_post.html', title='Новый пост', form=form, edit=False)


@app.route('/')
def home():
    try:
        db = db_session.create_session()
        posts = db.query(Post).all()[:-5:-1]
        return flask.render_template('home.html', title='ProjectsList', posts=posts)
    finally:
        db.close()


@app.route('/<category>')
@app.route('/<category>/<filter>')
def posts_list(category, filter='new'):
    try:
        db = db_session.create_session()
        if category == 'interesting':
            posts = db.query(Post).filter(Post.category=='Интересное')
        elif category == 'goodcode':
            posts = db.query(Post).filter(Post.category=='Хороший код')
        elif category == 'optimized':
            posts = db.query(Post).filter(Post.category=='Оптимизированное')
        elif category == 'beautifuldesign':
            posts = db.query(Post).filter(Post.category=='Красивый дизайн')
        elif category == 'new':
            posts = db.query(Post).all()[::-1]
        else:
            return '404'
        if category != 'new':
            if filter == 'best':
                posts = posts.order_by(-(Post.like - Post.dislike)).all()
            else:
                posts = posts.all()
        return flask.render_template('posts_list.html', title='Посты', posts=posts, category=category)
    finally:
        db.close()


@app.route('/post_like/<int:id>/<action>')
def post_like_action(id, action):
    try:
        db = db_session.create_session()
        post = db.query(Post).filter(Post.id == id).first()
        liked_user = db.query(User).filter(User.id==current_user.id).first()
        if not liked_user in post.users_who_liked:
            if action == 'like':
                post.like += 1
                action_in_int = 1
            else:
                post.dislike += 1
                action_in_int = -1
            post_rating = RatingPosts(user_id=liked_user.id, post_id=id, rating=action_in_int)
            db.add(post_rating)
            db.commit()
        else:
            post_rating = db.query(RatingPosts).filter(RatingPosts.user_id==liked_user.id, RatingPosts.post_id==id).first()
            if action == 'dislike' and post_rating.rating == 1:
                post_rating.rating = -1
                post.like -= 1
                post.dislike += 1
                db.commit()
            elif action == 'like' and post_rating.rating == -1:
                post_rating.rating = 1
                post.like += 1
                post.dislike -= 1
                db.commit()

        return flask.redirect(flask.request.referrer)
    finally:
        db.close()


@app.route('/comment_like/<int:id>/<action>')
def comment_like_action(id, action):
    try:
        db = db_session.create_session()
        comment = db.query(Comment).filter(Comment.id == id).first()
        liked_user = db.query(User).filter(User.id==current_user.id).first()
        if not liked_user in comment.users_who_liked:
            if action == 'like':
                comment.like += 1
                action_in_int = 1
            else:
                comment.dislike += 1
                action_in_int = -1
            comment_rating = RatingComments(user_id=liked_user.id, comment_id=id, rating=action_in_int)
            db.add(comment_rating)
            db.commit()
        else:
            comment_rating = db.query(RatingComments).filter(RatingComments.user_id==liked_user.id, RatingComments.comment_id==id).first()
            if action == 'dislike' and comment_rating.rating == 1:
                comment_rating.rating = -1
                comment.like -= 1
                comment.dislike += 1
                db.commit()
            elif action == 'like' and comment_rating.rating == -1:
                comment_rating.rating = 1
                comment.like += 1
                comment.dislike -= 1
                db.commit()
        return flask.redirect(flask.request.referrer)
    finally:
        db.close()


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
    info = get_repo_info(post.project_link)
    return flask.render_template('post_view.html', title=post.title, post=post, form=form, info=info)


@app.route('/user<int:id>/edit', methods=['GET', 'POST'])
def user_edit(id):
    if current_user.id == id:
        db = db_session.create_session()
        user = db.query(User).filter(User.id==id).first()
        form = RegisterForm()
        if not form.validate_on_submit():
            form.name.data = user.name
            form.info.data = user.info
            form.github.data = user.github
            form.image.data = open(user.image)
            form.mail.data = user.mail

            return flask.render_template('register.html', title='Изменить профиль', form=form, edit=True)
        else:
            user.name = form.name.data
            user.info = form.info.data
            user.github = form.github.data

            f = form.image.data
            if f:
                user.image = f'static/img/img{user.id}.jpg'
                image_stream = io.BytesIO(f.read())
                img = Image.open(image_stream)
                width, height = img.size
                if width > height:
                    delta = (width - height) // 2
                    img = img.crop((delta, 0, width - delta, height))
                else:
                    delta = (height - width) // 2
                    img = img.crop((0, delta, width, height - delta))
                img = img.resize((320, 320))
                img = img.convert('RGB')
                img.save(user.image)

            db.commit()
            return flask.redirect(f'/user{user.id}')
    else:
        return 'В доступе запрещено'


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

            return flask.render_template('add_post.html', title='Изменить пост', form=form, edit=True, post_id=id)
        else:
            post.title = form.title.data
            post.text = form.text.data
            post.project_link = form.project_link.data
            post.category = form.category.data
            db.commit()
            return flask.redirect(f'/posts/{id}')
    else:
        return 'В доступе запрещено'


@app.route('/posts/delete/<int:id>')
def post_delete(id):
    db = db_session.create_session()
    post = db.query(Post).filter(Post.id==id).first()
    db.delete(post)
    db.commit()
    return 'Пост удалён'


if __name__ == '__main__':
    db_session.global_init('db/database.db')
    app.run(port=8080, host='127.0.0.1')
