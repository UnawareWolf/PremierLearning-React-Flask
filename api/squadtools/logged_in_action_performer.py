import requests

from squadtools.squad import MANAGER_API

REDIRECT_URI = 'https://users.premierleague.com/'
LOGIN_URL = 'https://users.premierleague.com/accounts/login/'
PICK_TEAM_URL = 'https://fantasy.premierleague.com/my-team'
PICK_TEAM_API = 'https://fantasy.premierleague.com/api/my-team'
TRANSFERS_API = 'https://fantasy.premierleague.com/api/transfers/'
ME_API = 'https://fantasy.premierleague.com/api/me/'


def get_squad_ids(user_json):
    squad_ids = []
    for element in user_json['picks']:
        squad_ids.append(element['element'])
    return squad_ids


def get_user_jsons(username, password):
    user_json = {
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
    with requests.Session() as client:
        client.get(LOGIN_URL)
        login_response = login(client, username, password)
        if login_response.url == 'https://users.premierleague.com/?state=success':
            me_response = client.get(ME_API).json()['player']
            user_json['fpl_api']['manager_id'] = me_response['entry']
            user_json['fpl_api']['manager_json'] = client.get(MANAGER_API % user_json['fpl_api']['manager_id']).json()
            user_json['fpl_api']['picks'] = client.get('%s/%i/' % (PICK_TEAM_API, user_json['fpl_api']['manager_id'])).json()

            user_json['user']['name'] = me_response['first_name'] + ' ' + me_response['last_name']
            user_json['user']['loggedIn'] = True
            user_json['user']['teamIDs'] = get_squad_ids(user_json['fpl_api']['picks'])
    return user_json


def login(client, username, password):
    client.get(LOGIN_URL)
    login_data = dict(app='plusers', redirect_uri=REDIRECT_URI, login=username,
                      password=password, csrfmiddlewaretoken=client.cookies['csrftoken'])
    return client.post(LOGIN_URL, data=login_data)


def pick_team(request_payload, username, password):
    with requests.Session() as client:
        manager_id = login(client, username, password)
        client.get(PICK_TEAM_URL)
        client.post('%s/%i/' % (PICK_TEAM_API, manager_id), json=request_payload)


def make_transfers(request_payload, username, password):
    with requests.Session() as client:
        login(client, username, password)
        make_transfers_response = client.post(TRANSFERS_API, json=request_payload)
        print(make_transfers_response.url)
