from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()


class User(DB.Model):

    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String, nullable=False)
    username = DB.Column(DB.String, nullable=False)
    password = DB.Column(DB.String, nullable=False)

    def __repr__(self):
        return "<User: {}".format(self.name)