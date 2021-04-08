from datetime import datetime
from flask import Blueprint, request, session
from flask_cors import CORS
from squadtools import OptimiseRunner, do_login
from persistence import DB_Handler

bp = Blueprint('selection', __name__, url_prefix='/api')
CORS(bp)


@bp.route('/time', methods=(['GET']))
def get_time():
    return datetime.now()


@bp.route('/players', methods=(['GET']))
def get_all_players():
    db_handler = DB_Handler()
    players = db_handler.get_player_jsons()
    db_handler.close_connection()
    return {'players': players}


@bp.route('/optimise/login', methods=(['GET']))
def optimise_by_login():
    optimise_runner = OptimiseRunner(session['username'], session['password'])
    optimise_runner.run()
    return {'transfers': optimise_runner.get_transfers_json()}


@bp.route('/login', methods=(['POST']))
def login():
    request_data = request.get_json()
    user = do_login(request_data['username'], request_data['password'])
    if user['loggedIn']:
        session['username'] = request_data['username']
        session['password'] = request_data['password']
        session['loggedIn'] = True
    return {'user': user}


@bp.route('/teamids', methods=(['GET']))
def get_team_ids():
    if 'loggedIn' not in session or not session['loggedIn']:
        return {'teamIDs': []}
    optimise_runner = OptimiseRunner(session['username'], session['password'])
    optimise_runner.populate_squad()
    return {'teamIDs': optimise_runner.get_ids()}


@bp.route('/logout', methods=(['GET']))
def logout():
    session['username'] = ''
    session['password'] = ''
    session['loggedIn'] = False
    return {}
