from flask import Flask

from .optimise_runner import OptimiseRunner


if __name__ == '__main__':
    app = Flask(__name__)

    with app.app_context():
        opt = OptimiseRunner()
        opt.run()
        print(opt.get_transfers())
