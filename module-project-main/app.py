from flask import Flask, render_template, request, redirect, session, abort, url_for
from flask_login import LoginManager, login_user, logout_user, current_user
from flask_login.utils import login_required
from .signup import RegistrationForm, LoginForm, PredictionForm
from is_safe_url import is_safe_url
from .data_model import DB, User, Property, get_property
import pandas as pd
import joblib
import os
from datetime import datetime
from .train import get_at_it
from werkzeug.security import generate_password_hash
from .machine_learning import train

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
        #DB.drop_all()
        #DB.create_all()
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

    @app.route('/input', methods=['GET', 'POST'])
    @login_required
    def pre_input():
        form = PredictionForm()
        if request.method == 'POST' and form.validate:
            alpha = form.location.data
            beta = form.latitude.data
            gamma = form.longitude.data
            delta = form.score.data
            d = {'latitude': beta, 'longitude': gamma, 'review_scores_rating': delta}
            zeta = pd.DataFrame(data=d, index=[0])
            eta = get_at_it(alpha)
            theta = train(eta)
            iota = theta.predict(zeta)
            property = Property(location=str(alpha), latitude=beta, longitude=gamma, score=delta,
                                prediction=iota[0], user_id=current_user.id)
            DB.session.add(property)
            DB.session.commit()
            redirect('profile')
        return render_template('pre_input.html', form=form)

    @app.route('/logout')
    def logout():
        logout_user()
        return 'success'

    @app.route('/profile', methods=['GET', 'POST'])
    def show():
        alpha = Property.query.filter_by(user_id=current_user.id).first()
        dict = alpha.prediction
        return render_template('profile.html', alpha=dict)

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return 'database refreshed'

    return app
