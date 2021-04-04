from datetime import datetime
from flask import Blueprint, request, session
from flask_cors import CORS
from squadtools import OptimiseRunner
from persistence import DB_Handler

bp = Blueprint('selection', __name__, url_prefix='/api')
CORS(bp)


@bp.route('/players', methods=(['GET']))
def get_all_players():
    db_handler = DB_Handler()
    players = db_handler.get_player_jsons()
    db_handler.close_connection()
    return {'players': players}


@bp.route('/optimise/login', methods=(['GET', 'POST']))
def optimise_by_login():
    if request.method == 'GET':
        return {'time': datetime.now()}
    print(request.method)
    request_data = request.get_json()
    # print('username: %s, password: %s' % (username, password))
    session['username'] = request_data['username']

    # session['csrftoken'] = login_initial(request_data['username', request_data['password']])['csrftoken']
    # print(session['csrftoken'] + '\n')
    optimise_runner = OptimiseRunner(request_data['username'], request_data['password'])
    optimise_runner.run()
    
    return {'transfers': optimise_runner.get_transfers_json()}
