from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()


class Mango(DB.Model):

    id = DB.Column(DB.BigInteger, primary_key=True)
    name = DB.Column(DB.String, nullable=False)
    city = DB.Column(DB.String, nullable=False)
    country = DB.Column(DB.String, nullable=False)

    def __repr__(self):
        return "<User: {}".format(self.name)