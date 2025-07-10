from flask import Blueprint

bp = Blueprint('user_management', __name__, url_prefix='/users')

from app.user_management import routes
