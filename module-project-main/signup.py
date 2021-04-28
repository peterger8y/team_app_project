from wtforms import BooleanField, StringField, PasswordField, validators
from wtforms.validators import DataRequired, Email
from flask_wtf import FlaskForm


class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


class LoginTrue(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


#class LoginTrue(FlaskForm):
    #username = StringField('Username', validators=[Length(max=64)])
    #password = PasswordField('Password', validators=[Length(8, 16)])
    #remember = BooleanField('Remember Me')

    #def validate_username(self, field):
        #if not self.get_user():
            #raise ValidationError('Invalid username!')

    #def validate_password(self, field):
        #if not self.get_user():
           # return
        #if not self.get_user().check_password(field.data):
            #raise ValidationError('Incorrect password!')

    #def get_user(self):
        #return User.query.filter_by(username=self.username.data).first()
