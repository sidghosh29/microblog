'''
Flask-WTF is a thin wrapper around the WTForms package that nicely integrates it with Flask.
WTForms is a flexible forms validation and rendering library for Python web development. 
It can work with whatever web framework and template engine you choose. 
It supports data validation, CSRF (Cross-Site Request Forgery) protection, internationalization (I18N),
and more.
'''

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
'''
The above classes that represent the field types that I'm using for this form are imported directly
from the WTForms package, since the Flask-WTF extension does not provide customized versions.
'''
from wtforms.validators import ValidationError, DataRequired, Length
import sqlalchemy as sa
from flask_babel import _, lazy_gettext as _l
from app import db
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(
                User.username == username.data))
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))
