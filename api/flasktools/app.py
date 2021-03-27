import os

from flask import Flask
from flask_cors import CORS
from .selectionroute import bp as selection_bp


def create_app(test_config=None):
    """Create and configure the app"""
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    # app.config.from_mapping(
    #     SECRET_KEY="dev",
    #     DATABASE=os.path.join(app.instance_path, 'fantasy.db')
    # )

    app.register_blueprint(selection_bp)

    return app