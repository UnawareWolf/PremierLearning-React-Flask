from flask import Flask
from flask_cors import CORS
from .selection_route import bp as selection_bp
from persistence import close_connection


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)

    app.teardown_appcontext(close_connection)

    app.register_blueprint(selection_bp)

    return app
