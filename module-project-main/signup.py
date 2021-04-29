from wtforms import BooleanField, StringField, PasswordField, IntegerField, SelectField, FloatField, DateField, validators
from wtforms.validators import DataRequired, Email, ValidationError, Length
from flask_wtf import FlaskForm
from .data_model import User
from .train import list_locations



def validate_username(field):
    if User.query.filter_by(username=field.data).count() > 0:
        raise ValidationError('Username %s already exists!' % field.data)


class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


class LoginForm(FlaskForm):
    username = StringField('Username', [validators.Length(max=64)])
    password = PasswordField('Password', [validators.Length(6, 16)])

    def validate_username(self, field):
        if not self.get_user():
            raise ValidationError('Invalid username!')

    def validate_password(self, field):
        if not self.get_user():
            return
        if not self.get_user().check_password(field.data):
            raise ValidationError('Incorrect password!')

    def get_user(self):
        return User.query.filter_by(username=self.username.data).first()


class PredictionForm(FlaskForm):
    location = SelectField('City/Country', [validators.InputRequired()], choices=[x for x in list_locations])
    longitude = FloatField('Longitude', [validators.InputRequired()])
    latitude = FloatField('Longitude', [validators.InputRequired()])
    score = IntegerField('Avg Review Score (0-100)', [validators.InputRequired()])


