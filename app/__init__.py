'''
In Python, a subdirectory that includes a __init__.py file is considered a package, and can be imported.
When you import a package, the __init__.py executes and defines what symbols the package exposes to
the outside world.

'''
from flask import Flask
from config import Config
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
'''
The Flask-Login extension works with the application's user model, and expects 
certain properties and methods to be implemented in it. As long as these required items 
are added to the model, Flask-Login does not have any other requirements, so for example, 
it can work with user models that are based on any database system.

The four required items are listed below:

-is_authenticated: a property that is True if the user has valid credentials or False otherwise.
-is_active: a property that is True if the user's account is active or False otherwise.
-is_anonymous: a property that is False for regular users, and True only for a special, anonymous user.
-get_id(): a method that returns a unique identifier for the user as a string.

Flask-Login provides a mixin class called UserMixin that includes safe implementations that are appropriate 
for most user model classes.
'''

import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

from flask_mail import Mail

from flask_moment import Moment

# Load environment variables from .env
load_dotenv()

app = Flask(__name__) 
'''The __name__ variable passed to the Flask class is a Python predefined variable, which is set to the name of the module
 in which it is used. Flask uses the location of the module passed here as a starting point when it needs to load associated
   resources such as template files'''

app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
mail = Mail(app)
moment = Moment(app)

if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
          mailhost = (app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
          fromaddr='sidghosh8953@' + app.config['MAIL_SERVER'],
          toaddrs=app.config['ADMINS'], subject='Microblog Failure',
          credentials=auth, secure=secure)
        
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,backupCount=10) 
    # Once the log reaches its size limit of 10 KB, it will rename the current log file and create a new log file
    # Keeps only the last 10 log files (backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

from app import routes, models, errors
'''
The bottom import is a well known workaround that avoids circular imports, a common problem with Flask applications.
'''