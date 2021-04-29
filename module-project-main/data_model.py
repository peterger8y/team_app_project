from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

DB = SQLAlchemy()


class User(DB.Model, UserMixin):
    id = DB.Column(DB.Unicode(100), primary_key=True)
    username = DB.Column(DB.String, nullable=False)
    email = DB.Column(DB.String, nullable=False)
    password = DB.Column(DB.String, nullable=False)

    def check_password(self, password):
        if not password == self.password:
            return False
        else:
            return True


class Property(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    location = DB.Column(DB.String, nullable=False)
    neighbourhood = DB.Column(DB.String, nullable=False)
    experience = DB.Column(DB.String, nullable=False)
    score = DB.Column(DB.Integer, nullable=False)
    user_id = DB.Column(DB.Unicode(100), DB.ForeignKey('user.id'))
    user = DB.relationship("User", backref=DB.backref("properties", lazy=True))


def get_property(user_id):
    query = Property.query.filter_by(Property.user_id == user_id)
    return query
