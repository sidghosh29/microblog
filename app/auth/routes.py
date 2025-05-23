from flask import render_template, redirect, url_for, flash, request
from urllib.parse import urlsplit
from flask_login import login_user, logout_user, current_user
from flask_babel import _
import sqlalchemy as sa
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email



@bp.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    '''
    Even though a new LoginForm instance is created when a post request is made, it doesn't mean it starts from a blank state. 
    The form is immediately populated with the data from the current request upon creation.
    WTForms automatically binds the form fields to data from the current request (i.e., request.form if it's a POST request).
    '''
    if form.validate_on_submit():
        # flash('Login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data))
        '''
        The flash() function is a useful way to show a message to the user. A lot of applications use this
        technique to let the user know if some action has been successful or not. In this case, I'm going to
        use this mechanism as a temporary solution, because I don't have all the infrastructure necessary to 
        log users in for real yet. The best I can do for now is show a message that confirms that the application
        received the credentials.
        
        When you call the flash() function, Flask stores the message, but flashed messages will not magically 
        appear in web pages. The templates of the application need to render these flashed messages in a way 
        that works for the site layout. These messages will be added to the base template.

        An interesting property of these flashed messages is that once they are requested once through the get_flashed_messages
        function they are removed from the message list, so they appear only once after the flash() function is called.
        '''
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '': 
            next_page = url_for('main.index')
            # Checking urlsplit(next_page).netloc != '' protects the app from Open Redirect Attacks and Phishing Attacks.
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)



@bp.route('/logout')
def logout():
    logout_user()
    response = redirect(url_for('auth.login'))
    return response


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)

    

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data))
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', form=form)



