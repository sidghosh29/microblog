import os
from dotenv import load_dotenv

#print(__file__) ---> __file__ is the file path to the current file
#print(os.path.dirname(__file__)) ---> os.path.dirname(<filepath>) will return the folder path

basedir = os.path.abspath(os.path.dirname(__file__))
# Load environment variables from .env
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess' # class variable
    '''
    Flask and some of its extensions use the value of the secret key as a cryptographic key,
    useful to generate signatures or tokens. 

    The Flask-WTF extension uses it to protect web forms against a nasty attack called 
    Cross-Site Request Forgery or CSRF (pronounced "seasurf"). As its name implies, the secret key
    is supposed to be secret, as the strength of the tokens and signatures generated with it depends
    on no person outside the trusted maintainers of the application knowing it.

    SECRET_KEY in Flask is used for securely signing session cookies and is also crucial for CSRF protection
    when using Flask-WTF or other CSRF protection mechanisms. 
    - When a user submits a form, Flask-WTF generates a CSRF token using SECRET_KEY.
    - This token is included in the form and must match the one stored in the session when submitted.
    - If an attacker tries to forge a request, they won’t have the valid token, and the request gets rejected.

    '''
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db') # class variable
    
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['siddghosh8953@gmail.com']

    POSTS_PER_PAGE = 2

    LANGUAGES = ['en', 'es', 'de', 'hi']

    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')

    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')