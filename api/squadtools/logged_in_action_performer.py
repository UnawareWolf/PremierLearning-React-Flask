import requests
import json

REDIRECT_URI = 'https://users.premierleague.com/'
LOGIN_URL = 'https://users.premierleague.com/accounts/login/'
PICK_TEAM_URL = 'https://fantasy.premierleague.com/my-team'
PICK_TEAM_API = 'https://fantasy.premierleague.com/api/my-team'
TRANSFERS_API = 'https://fantasy.premierleague.com/api/transfers/'


def login(client):
    client.get(LOGIN_URL)
    with open('../.vscode/fantasy_login.json') as json_file:
        fantasy_login = json.load(json_file)
    login_data = dict(app='plusers', redirect_uri=REDIRECT_URI, login=fantasy_login['EMAIL'],
                      password=fantasy_login['PASSWORD'], csrfmiddlewaretoken=client.cookies['csrftoken'])
    login_response = client.post(LOGIN_URL, data=login_data)
    print(login_response.url)


def pick_team(team_id, request_payload):
    with requests.Session() as client:
        login(client)
        client.get(PICK_TEAM_URL)
        client.post('%s/%i/' % (PICK_TEAM_API, team_id), json=request_payload)


def get_player_ids(team_id):
    with requests.Session() as client:
        login(client)
        return client.get('%s/%i/' % (PICK_TEAM_API, team_id))


def make_transfers(request_payload):
    with requests.Session() as client:
        login(client)
        # client.get(PICK_TEAM_URL)
        make_transfers_response = client.post(TRANSFERS_API, json=request_payload)
        print(make_transfers_response.url)
