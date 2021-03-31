from flask import Flask

from .runner import Runner

if __name__ == '__main__':
    app = Flask(__name__)

    with app.app_context():
        for i in range(1):
            runner = Runner()
            runner.run()
