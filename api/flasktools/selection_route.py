from datetime import datetime
from flask import Blueprint, request, session
from flask_cors import CORS
from squadtools import OptimiseRunner

bp = Blueprint('time', __name__, url_prefix='/api/time')
CORS(bp)

@bp.route('/', methods=(['GET', 'POST']))
def time_test():
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
    return {'transfers': optimise_runner.get_transfers()}
