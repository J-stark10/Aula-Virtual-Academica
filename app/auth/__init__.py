from flask import Blueprint

bp_auth = Blueprint("auth", __name__, url_prefix="/auth", template_folder="templates")

from app.auth import routes
