import datetime
from flask import Flask

app = Flask(__name__)

@app.route('/api/time')
def get_current_time():
    return {'time': datetime.datetime.now()}
