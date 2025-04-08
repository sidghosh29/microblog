'''
In Python, a subdirectory that includes a __init__.py file is considered a package, and can be imported.
When you import a package, the __init__.py executes and defines what symbols the package exposes to
the outside world.

'''
from flask import Flask, request
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
from flask_babel import Babel, lazy_gettext as _l
def get_locale():
    # return request.accept_languages.best_match(app.config['LANGUAGES'])
    return 'de'

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
login.login_message = _l('Please log in to access this page.')

mail = Mail(app)
moment = Moment(app)
babel = Babel(app, locale_selector=get_locale)

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
###
'''
before_request, after_request, teardown_request → 
These are called Request Lifecycle Hooks because they're tied specifically to the lifecycle of handling a request.

context_processor, template_global, etc. → 
These are often lumped in with "lifecycle hooks" more broadly, because they also let you hook into Flask's behavior 
at specific points (like rendering templates).

@app.before_request: Runs before each request is processed.
@app.context_processor: Injects variables or functions into the template context.
@app.teardown_request: Runs after the request is processed, typically for cleanup.
Flask extensions like Babel use these hooks to integrate their functionality seamlessly into the app.
'''
###
'''
Use pybabel extract -F babel.cfg -k _l -o messages.pot . command on terminal to 
extract all marked translatable strings (including _l() and default _()) from source files 
using babel.cfg, and saves them to messages.pot.

pybabel init -i messages.pot -d app/translations -l es command on terminal to initialize a new translation folder
The command will create a es subdirectory inside this directory for the Spanish data files. 
In particular, there will be a new file named app/translations/es/LC_MESSAGES/messages.po, 
that is where the translations need to be made.

pybabel compile -d app/translations is then used to compile the new po files to mo files. 
The .mo file is the file that Flask-Babel will use to load translations for the application.

-> pybabel extract -F babel.cfg -k _l -o messages.pot . can again be used if you add some more markers.
-> pybabel update -i messages.pot -d app/translations is used to update the translation files. This is 
going to be an intelligent merge, in which any existing texts will be left alone, while only entries that 
were added or removed in messages.pot will be affected.
'''