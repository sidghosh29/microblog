# microblog.py is the entry point of the application. 
# This is the main script that runs the application.

from app import create_app, db
import sqlalchemy as sa
import sqlalchemy.orm as so
from app.models import User, Post

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Post': Post}

'''
Refer to point 5 in 'Notes' for more details on app.shell_context_processor. 
'''
###

'''
Refer to point 3 in 'Notes' for more details on what 'flask run' command does.
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
