from flask import Flask, render_template, request
from decouple import config
from data_model import DB, User
from inside_airbnb import InsideAirBnB

DATABASE_URL = config('DATABASE_URL')


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    DB.init_app(app)

    @app.route('/')
    def landing():
        DB.create_all()
        airbnb = InsideAirBnB()
        location_names = airbnb.get_location_names()  # for use in a dropdown
        return render_template('landingPage.html')

    @app.route('/login')
    def form():
        return render_template('login.html')

    @app.route('/data', methods=['POST', 'GET'])
    def data():

        if request.method == 'GET':
            return f"The URL /data is accessed directly. Try going to '/login' to submit form"
        if request.method == 'POST':
            username = request.form['Username']
            password = request.form['Password']
            alpha = User.query.filter_by(username=username, password=password).all()
            if alpha == 0:
                return render_template('sign_in_fail.html')
            else:
                return render_template('login_success.html')

    @app.route('/signup_check', methods=['POST', 'GET'])
    def data2():
        if request.method == 'GET':
            return f"the URL /data2 is accessed directly. Try going to '/' to submit tweet input"
        if request.method == 'POST':
            form_data = request.form
            name = request.form['Name']
            username = request.form['Username']
            password = request.form['Password']
            a = User.query.filter_by(username=username).all()
            if len(a) != 0:
                return render_template('user_gen_fail.html')
            else:
                info = User(name=name, username=username, password=password)
                DB.session.add(info)
                DB.session.commit()
                return render_template('user_signup_confirmation.html', form_data=form_data, name=name)

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return 'database refreshed'

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
