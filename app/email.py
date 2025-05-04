from flask import current_app
from flask_mail import Message
from app import mail
from threading import Thread
# Python has support for running asynchronous tasks, actually in more than one way. 
# The threading and multiprocessing modules can both do this.

def send_async_email(app, msg):
    with app.app_context():
        # Flask's app context is needed because new threads don’t automatically inherit it. 
        # When send_async_email runs in a separate thread, it lacks access to Flask’s config and extensions. 
        # Using with app.app_context(): ensures the thread can safely use mail.send(msg).
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body, cc=["siddghosh8953@gmail.com"], attachments=None, sync=False):
    msg = Message(subject, sender=sender, recipients=recipients, cc=cc)
    msg.body = text_body
    msg.html = html_body
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    if sync:
        mail.send(msg) 
        # Revert back to calling mail.send(msg) directly when sync is True.
    else:
        Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
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