from flask import render_template
from app import db
from app.errors import bp

# In the handlers.py module, instead of attaching the error handlers to the application with 
# the @app.errorhandler decorator, we use the blueprint's @bp.app_errorhandler decorator.
@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500