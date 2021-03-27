import datetime

from flask import Blueprint
from flask_cors import CORS
from squadtools import OptimiseRunner

bp = Blueprint('time', __name__, url_prefix='/api/time')
CORS(bp)

@bp.route('/', methods=('GET',))
def time_test():
    optimise_runner = OptimiseRunner()
    optimise_runner.run()
    return {'time': optimise_runner.get_a_player()}
    # return {'time': datetime.datetime.now()}
