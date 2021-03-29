import json

from flask import Flask

from .optimise_runner import OptimiseRunner


if __name__ == '__main__':
    app = Flask(__name__)

    with open('../.vscode/fantasy_login.json') as json_file:
        fantasy_login = json.load(json_file)
    with app.app_context():
        opt = OptimiseRunner(fantasy_login['ID'], fantasy_login['EMAIL'], fantasy_login['PASSWORD'])
        opt.run()
        print(opt.get_transfers())
