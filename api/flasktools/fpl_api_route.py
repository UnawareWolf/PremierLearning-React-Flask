import requests

from datetime import datetime
from flask import Blueprint, request, session
from flask_cors import CORS
from squadtools import OptimiseRunner, get_user_jsons
from persistence import DB_Handler

bp = Blueprint('login', __name__, url_prefix='/')
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


@bp.route('/gw', methods=(['GET']))
def get_current_gw():
    return requests.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()


@bp.route('/team', methods=(['GET']))
def optimise_by_login():
    if 'user_json' not in session:
        return {'transfers': None}
    optimise_runner = OptimiseRunner(session['user_json'])
    optimise_runner.run()
    return {'transfers': optimise_runner.get_transfers_json()}


@bp.route('/login', methods=(['POST']))
def login():
    request_data = request.get_json()

    session['user_json'] = get_user_jsons(request_data['username'], request_data['password'])
    return {'user': session['user_json']['user']}


@bp.route('/logout', methods=(['GET']))
def logout():
    session['user_json'] = {
        'user': {
            'name': '',
            'loggedIn': False,
            'teamIDs': []
        },
        'fpl_api': {
            'manager_id': None,
            'manager_json': None,
            'picks': None
        }
    }
    return {}

@bp.route('/opt', methods=(['GET']))
def optimise_by_login_2():
    if 'user_json' not in session:
        return {'transfers': None, 'suggestedTeams': None}
    optimise_runner = OptimiseRunner(session['user_json'])
    optimise_runner.run()
    transfers = optimise_runner.get_transfers_json()
    suggestedTeams = optimise_runner.get_future_starting_teams()
    return {
        'transfers': transfers,
        'suggestedTeams': suggestedTeams
    }
