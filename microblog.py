# microblog.py is the entry point of the application. 
# This is the main script that runs the application.

from app import create_app, db
import sqlalchemy as sa
import sqlalchemy.orm as so
from app.models import User, Post, Notification, Message, Task

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Post': Post, 'Message': Message, 'Notification': Notification, 'Task': Task}

'''
Refer to point 5 in 'Notes' for more details on app.shell_context_processor. 
'''
###

'''
Refer to point 3 in 'Notes' for more details on what 'flask run' command does.
'''

if __name__=="__main__":
    app.run(debug=True, port=5001)