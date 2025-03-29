'''
Flask-WTF is a thin wrapper around the WTForms package that nicely integrates it with Flask.
WTForms is a flexible forms validation and rendering library for Python web development. 
It can work with whatever web framework and template engine you choose. 
It supports data validation, CSRF (Cross-Site Request Forgery) protection, internationalization (I18N),
and more.
'''

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
'''
The four classes that represent the field types that I'm using for this form are imported directly
from the WTForms package, since the Flask-WTF extension does not provide customized versions.
'''
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length

import sqlalchemy as sa
from app import db
from app.models import User

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Repeat Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')

    '''
    Stock validators are predefined validators that come with WTForms such as DataRequired, Email, EqualTo, etc.
    When you add any methods that match the pattern validate_<field_name>, WTForms takes those as custom validators 
    and invokes them in addition to the stock validators.s
    '''
 
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username
    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
            if user is not None:
                raise ValidationError('Please use a different username.')