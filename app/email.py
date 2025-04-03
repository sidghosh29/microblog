from flask_mail import Message
from app import mail, app
from flask import render_template
from threading import Thread
# Python has support for running asynchronous tasks, actually in more than one way. 
# The threading and multiprocessing modules can both do this.

def send_async_email(app, msg):
    with app.app_context():
        # Flask's app context is needed because new threads don’t automatically inherit it. 
        # When send_async_email runs in a separate thread, it lacks access to Flask’s config and extensions. 
        # Using with app.app_context(): ensures the thread can safely use mail.send(msg).
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body, cc=["siddghosh8953@gmail.com"]):
    msg = Message(subject, sender=sender, recipients=recipients, cc=cc)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()
    # mail.send(msg)
    '''
    There are two types of contexts, the application context and the request context. 
    In most cases, these contexts are automatically managed by the Flask, but when the application starts custom threads, 
    contexts for those threads may need to be manually created.

    The reason many extensions need to know the application instance is because they have their configuration stored in 
    the app.config object. This is exactly the situation with Flask-Mail.

    The mail.send() method needs to access the configuration values for the email server, and that can only be done by 
    knowing what the application is. The application context that is created with the with app.app_context() call makes 
    the application instance accessible via the current_app variable from Flask.
    '''

def send_password_reset_email(user):
    print("Triggering send_password_reset_email function")
    token = user.get_reset_password_token()
    send_email('[Microblog] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))