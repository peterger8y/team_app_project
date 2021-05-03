from flask import Flask, render_template, request, redirect, session, abort, url_for
from flask_login import LoginManager, login_user, logout_user, current_user
from flask_login.utils import login_required
from .signup import RegistrationForm, LoginForm, PredictionForm
from .data_model import DB, User, Property
import pandas as pd
import os
from datetime import datetime
from .train import get_at_it
from werkzeug.security import generate_password_hash
from .machine_learning import train
from flask_wtf import FlaskForm
from wtforms import SelectField, validators
import plotly.express as px

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
    def begin():
        return redirect('/landing')

    @app.route('/landing', methods=['GET', 'POST'])
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
    def pre_input():
        form = PredictionForm()
        if request.method == 'POST' and form.validate:
            alpha = form.location.data
            beta = form.latitude.data
            gamma = form.longitude.data
            delta = form.score.data
            name = form.name.data
            d = {'latitude': beta, 'longitude': gamma, 'review_scores_rating': delta}
            zeta = pd.DataFrame(data=d, index=[0])
            eta = get_at_it(alpha)
            theta = train(eta)
            iota = theta.predict(zeta)
            property1 = Property(location=str(alpha), latitude=beta, longitude=gamma, score=delta,
                                 prediction=iota[0], name=name, user_id=current_user.id)
            DB.session.add(property1)
            DB.session.commit()
            return redirect('profile')
        return render_template('pre_input.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return render_template('logout.html')

    @app.route('/profile', methods=['GET', 'POST'])
    def show():
        dict_list = []
        if current_user.is_authenticated:
            alpha = Property.query.filter_by(user_id=current_user.id).all()
            for x in alpha:
                delta = {'property_#': x.id, 'location': x.location, 'latitude': x.latitude, 'longitude': x.longitude,
                         'score': x.score, 'optimized price': x.prediction, 'name': x.name}
                dict_list.append(delta)
            choices = []
            for x in dict_list:
                choices.append(x['name'])

            class PropertySelector(FlaskForm):
                name = SelectField('Name of Property/Identifier', [validators.InputRequired()],
                                   choices=choices)

            form = PropertySelector()

        return render_template('profile.html', alpha=dict_list, form=form)

    @app.route('/data_insight', methods=['GET', 'POST'])
    def more_data():
        name = request.form['name']
        property = Property.query.filter_by(name=name).first()
        location = property.location
        fee, fie = get_at_it(location=location, geo=True)
        fie['neighbourhood'] = fie.index
        fig = px.choropleth(fie, geojson=fee, color="price",
                            locations="neighbourhood", featureidkey="properties.neighbourhood",
                            projection="mercator"
                            )
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        fig.write_html("module-project-main/templates/image_win.html", include_plotlyjs=False)
        return render_template('image_win.html')

    @app.route('/message_received')
    def received():
        return render_template('received.html')

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return 'database refreshed'

    return app
