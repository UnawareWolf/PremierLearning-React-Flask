import os

from flask import Flask
from flask_cors import CORS
from .fpl_api_route import bp as fpl_api_bp
from persistence import close_connection

# set up next gameweek number as global or something to save reading it from a file for every user
# at least read it from db instead


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    app.config.from_mapping(SECRET_KEY=os.urandom(16))

    app.teardown_appcontext(close_connection)

    app.register_blueprint(fpl_api_bp)

    return app
