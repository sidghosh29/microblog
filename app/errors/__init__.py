# In the context of a Blueprint package in Flask, the “base module” usually 
# refers to the module where the Blueprint instance is created and configured.
# Therefore, this __init__.py file inside the errors package is the base module
# for the errors blueprint.

from flask import Blueprint

bp = Blueprint('errors', __name__)

from app.errors import handlers