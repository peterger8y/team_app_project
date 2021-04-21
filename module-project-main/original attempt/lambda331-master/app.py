from flask import Flask, render_template, request
import json
from .data_model import DB, Mango
from os import path

def create_app():


    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    DB.init_app(app)

    @app.route('/')
    def landing():
        if not path.exists(app.config['SQLALCHEMY_DATABASE_URI']):
            DB.drop_all()
            DB.create_all()
        return render_template('base.html')

    @app.route('/form')
    def form():
        return render_template('form.html')

    @app.route('/data', methods=['POST', 'GET'])
    def data():

        if request.method == 'GET':
            return f"The URL /data is accessed directly. Try going to '/form' to submit form"
        if request.method == 'POST':
            form_data = request.form

            return render_template('data.html', form_data=form_data)
    @app.route('/data2', methods=['POST', 'GET'])
    def data2():
        if request.method == 'GET':
            return f"the URL /data2 is accessed directly. Try going to '/' to submit tweet input"
        if request.method == 'POST':
            form_data = request.form
            id = request.form['ID']
            name = request.form['Name']
            city = request.form['City']
            country = request.form['Country']
            info = Mango(id=id, name=name, city=city, country=country)
            DB.session.add(info)
            DB.session.commit()

            return render_template('data2.html', form_data=form_data, name=name)

    return app

