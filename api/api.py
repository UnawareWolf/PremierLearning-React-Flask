# import datetime
# from flask import Flask
from flasktools import create_app

# app = Flask(__name__)

if __name__ == '__main__':
    app = create_app()
    app.run(debug=False)

# @app.route('/api/time')
# def get_current_time():
#     return {'time': datetime.datetime.now()}
