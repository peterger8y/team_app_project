from flask import Flask, render_template, request, redirect, session, abort, url_for
from flask_login import LoginManager, login_user, logout_user
from flask_login.utils import login_required
from .signup import RegistrationForm, LoginForm, PredictionForm
from is_safe_url import is_safe_url
from .data_model import DB, User, get_property
import pandas as pd
import joblib
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.environ['SECRET_KEY']
    DB.init_app(app)
    login_manager.init_app(app)

    @app.route('/')
    def landing():
        # DB.drop_all()
        # DB.create_all()
        return render_template('landing.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegistrationForm(request.form)
        if request.method == 'POST' and form.validate():
            now = datetime.now()
            id1 = generate_password_hash(str(now))
            user = User(id=id1, username=form.username.data, email=form.email.data,
                        password=form.password.data)
            check = User.query.filter(User.email == form.email.data).first()
            if check:
                return 'email already in use'
            check = User.query.filter(User.username == form.username.data).first()
            if check:
                return 'username already in use...'
            DB.session.add(user)
            DB.session.commit()
            return redirect('/login')
        return render_template('register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if request.method == 'POST' and form.validate_on_submit():
            # Login and validate the user.
            check = User.query.filter(
                User.username == form.username.data and User.password == form.username.data).first()
            if check:
                user = LoginForm(username=form.username.data, password=form.password.data).get_user()
                login_user(user)
                # next1 = request.args.get('next')
                # if not is_safe_url(next1):
                # return abort(400)
                return redirect('/profile')
            else:
                return 'login fail'
        return render_template('login.html', form=form)

    @app.route('/input')
    def input_info():
        form = PredictionForm()
        return render_template('predict.html', form=form)

    @app.route('/result', methods=['GET', 'POST'])
    def results():
        if request.method == 'GET':
            return f"the URL /result is accessed directly. Try going to '/predict' to submit metrics"
        if request.method == 'POST':
            metric1 = request.form['Date Commenced Hosting']
            metric2 = request.form['Neighborhood']
            metric3 = request.form['Avg Review Score Rating(out of 100)']
            predictor = joblib.load('./pipe_model2.joblib')
            d = {'host_since': metric1, 'neighbourhood_group_cleansed': metric2, 'review_scores_rating': metric3}
            row = pd.DataFrame(data=d, index=[0])
            alpha = predictor.predict(row)
            return str(alpha)

    @app.route('/logout')
    def logout():
        logout_user()
        return 'success'

    @app.route('/profile', methods=['GET', 'POST'])
    def show():
        return render_template('profile.html')

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return 'database refreshed'

    return app
