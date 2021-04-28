from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

DB = SQLAlchemy()


class User(DB.Model, UserMixin):

    id = DB.Column(DB.Unicode(100), primary_key=True)
    username = DB.Column(DB.String, nullable=False)
    email = DB.Column(DB.String, nullable=False)
    password = DB.Column(DB.String, nullable=False)

    def __init__(self, **kwargs):
        password = kwargs.pop('password')
        password = generate_password_hash(password)
        kwargs['password'] = password
        super(User, self).__init__(**kwargs)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_json(self):
        return {'id': self.id, 'username': self.username}