from flask import Flask, render_template, redirect, request, abort
from flask_restful import Api

from api import JokeListResource, JokeResource
from data import db_session
from form.joke import JokeForm
from form.login import LoginForm
from form.register import RegisterForm
from data.user import User
from data.joke import Joke
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['DEBUG'] = True

db_session.global_init("db/data.db")

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


api = Api(app)
api.add_resource(JokeListResource, '/api/v1/joke')
api.add_resource(JokeResource, '/api/v1/joke/<int:id>')


@app.route('/')
def index():
    db_sess = db_session.create_session()
    jokes = db_sess.query(Joke).all()
    return render_template('index.html', jokes=jokes)


@app.route('/joke',  methods=['GET', 'POST'])
@login_required
def add_joke():
    form = JokeForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        joke = Joke(
            title=form.title.data,
            text=form.text.data,
            user_id=current_user.id
        )
        db_sess.add(joke)
        db_sess.commit()
        return redirect('/')
    return render_template('joke.html', title='Добавить шутку', form=form)


@app.route('/joke/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_joke(id):
    form = JokeForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        joke = db_sess.query(Joke).filter(Joke.id == id, Joke.user == current_user).first()
        if joke:
            form.title.data = joke.title
            form.text.data = joke.text
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        joke = db_sess.query(Joke).filter(Joke.id == id, Joke.user == current_user).first()
        if joke:
            joke.title = form.title.data
            joke.text = form.text.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('joke.html', title='Изменить шутку', form=form)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def joke_delete(id):
    db_sess = db_session.create_session()
    joke = db_sess.query(Joke).filter(Joke.id == id, Joke.user == current_user).first()
    if joke:
        db_sess.delete(joke)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/like/<int:id>')
@login_required
def joke_like(id):
    db_sess = db_session.create_session()
    joke = db_sess.query(Joke).filter(Joke.id == id).first()
    if joke:
        user = db_sess.merge(current_user)
        if user in joke.likes:
            joke.likes.remove(user)
        else:
            joke.likes.append(user)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    app.run()