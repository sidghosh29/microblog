'''
To complete the application, you need to have a Python script at the top-level that 
defines the Flask application instance. Let's call this script microblog.py, and define
it as a single line that imports the application instance:
'''
from app import create_app, db
import sqlalchemy as sa
import sqlalchemy.orm as so
from app.models import User, Post

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Post': Post}

'''
The app.shell_context_processor decorator registers the function as a shell context function. 
When the flask shell command runs, it will invoke this function and register the items returned 
by it in the shell session. The reason the function returns a dictionary and not a list is that 
for each item you have to also provide a name under which it will be referenced in the shell, 
which is given by the dictionary keys.
'''
###


'''
The flask run command will look for a Flask application instance in the module referenced by the 
FLASK_APP environment variable, which in this case is 'microblog.py'. The command sets up a web server
that is configured to forward requests to this application.

When you run flask run without setting the FLASK_APP environment variable, Flask looks for an application instance
in a file named app.py or wsgi.py within the current directory. If it finds the application instance (app), Flask
initializes the application. The application context, which includes configuration, routes, and other components,
is created only when needed—such as during a request or when explicitly pushed (app.app_context().push()).
'''

###

'''
'python-dotenv' package is used to load environment variables from a .env (or in our case .flaskenv) file 
into the environment variables of your project. 
It reads key-value pairs from a .env file and sets them as environment variables in your application. 
Flask allows you to register environment variables that you want to be automatically used when you run 
the flask command using this 'python-dotenv' package and having all the environment variables in .flaskenv file.

While .flaskenv is specifically recognized and loaded by Flask, it's a common practice to store 
environment variables in a file named .env. Flask does not load .env automatically unless you 
specifically use a package like python-dotenv to load it. However, if you have a .flaskenv file,
Flask will handle this for you.
'''

###

'''
class sqlalchemy.schema.Column, class sqlalchemy.types.Integer

When we use db.Column or db.Integer, we are actually referring to the above sqlalchemy classes
'''
if __name__=="__main__":
    app.run(debug=True, port=5001)

'''
Applications deployed on production web servers typically listen on port 443, or sometimes 80 
if they do not implement encryption, but access to these ports requires administration rights. 
Since this application is running in a development environment, Flask uses port 5000 by default.
Here I am using 5001.

Alternatively, you can use the following command: flask run --port 5001
'''


'''
FYI: The with statement can only be used with objects that implement the context manager protocol, 
meaning they have both __enter__() and __exit__() methods. These objects are called context managers.
'''
