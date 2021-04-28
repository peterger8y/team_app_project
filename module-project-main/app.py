from flask import Flask, render_template, request, redirect, session, abort, url_for, flash
from flask_login import LoginManager, login_user, logout_user
from .signup import RegistrationForm, LoginTrue
from is_safe_url import is_safe_url
from .data_model import DB, User
import pandas as pd
import joblib
import os

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
        DB.drop_all()
        DB.create_all()
        return render_template('landing.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegistrationForm(request.form)
        if request.method == 'POST' and form.validate():
            id1 = str(form.username.data) + str(form.email.data) + form.password.data
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
            flash('Thanks for registering')
            return redirect('/login')
        return render_template('register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginTrue()
        if request.method == 'POST' and form.validate_on_submit():
            # Login and validate the user.
            check = User.query.filter(User.username == form.username.data and User.password == form.username.data).first()
            if check:
                user = User(username=form.username.data, password=form.password.data)
                login_user(user)
                flash('Logged in successfully.')
                next1 = request.args.get('next')
                if not is_safe_url(next1):
                    return abort(400)
            else:
                flash('login failure')
                return 'login fail'
        return render_template('login.html', form=form)

    @app.route('/input')
    def input_info():
        return render_template('predict_input.html')

    @app.route('/result', methods=['POST', 'GET'])
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

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return 'database refreshed'

    return app
