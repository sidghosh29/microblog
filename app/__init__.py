'''
In Python, a subdirectory that includes a __init__.py file is considered a package, and can be imported.
When you import a package, the __init__.py executes and defines what symbols the package exposes to
the outside world.

'''
from flask import Flask, request, current_app

# The current_app variable that Flask provides is a special "context" variable that 
# Flask initializes with the application before it dispatches a request.

from config import Config
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
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])
    # return 'de'

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page.')
mail = Mail()
moment = Moment()
babel = Babel()


# Having the application as a global variable introduces some complications, mainly in the form of limitations 
# for some testing scenarios. Therefore we use a factory function instead. 

def create_app(config_class=Config):
    app = Flask(__name__)
    '''
    The __name__ variable passed to the Flask class is a Python predefined variable, which is set to the name of the module 
    in which it is used. Flask uses the location of the module passed here as a starting point when it needs to load associated 
    resources such as template files
    '''

    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    babel.init_app(app, locale_selector=get_locale)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    '''
    When a blueprint is registered, any view functions, templates, static files, error handlers, etc. 
    are connected to the application.'''

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.cli import bp as cli_bp
    app.register_blueprint(cli_bp)


    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/microblog.log',
                                           maxBytes=10240, backupCount=10)
        # Once the log reaches its size limit of 10 KB, it will rename the current log file and create a new log file
        # Keeps only the last 10 log files (backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')

    return app

from app import models

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