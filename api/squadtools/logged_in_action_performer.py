import requests
import json

REDIRECT_URI = 'https://users.premierleague.com/'
LOGIN_URL = 'https://users.premierleague.com/accounts/login/'
PICK_TEAM_URL = 'https://fantasy.premierleague.com/my-team'
PICK_TEAM_API = 'https://fantasy.premierleague.com/api/my-team'
TRANSFERS_API = 'https://fantasy.premierleague.com/api/transfers/'
ME_API = 'https://fantasy.premierleague.com/api/me/'


def login(client, username, password):
    client.get(LOGIN_URL)
    # with open('../.vscode/fantasy_login.json') as json_file:
    #     fantasy_login = json.load(json_file)
    # login_data = dict(app='plusers', redirect_uri=REDIRECT_URI, login=fantasy_login['EMAIL'],
    #                   password=fantasy_login['PASSWORD'], csrfmiddlewaretoken=client.cookies['csrftoken'])
    login_data = dict(app='plusers', redirect_uri=REDIRECT_URI, login=username,
                      password=password, csrfmiddlewaretoken=client.cookies['csrftoken'])
    login_response = client.post(LOGIN_URL, data=login_data)
    print(client.cookies)
    manager_id = client.get(ME_API).json()['player']['entry']
    # print(me_response.json()['player']['entry'])
    print(manager_id)
    print(login_response.url)
    return manager_id


# def login_initial(username, password):
#     with requests.Session() as client:
#         client.get(LOGIN_URL)
        
#         login_response = client.post(LOGIN_URL, data=dict(app='plusers', redirect_uri=REDIRECT_URI, login=username,
#                         password=password, csrfmiddlewaretoken=client.cookies['csrftoken']))
#         print(login_response.url)
        
#         return {'manager_id': client.get(ME_API).json()['player']['entry'],
#                 'csrftoken': client.cookies['csrftoken']}


# def login_existing(client, csrftoken):
#     client.get(LOGIN_URL)
#     client.post(LOGIN_URL,
#                 data = dict(app='plusers', redirect_uri=REDIRECT_URI,
#                 csrfmiddlewaretoken=csrftoken))
#     return client.get(ME_API).json()['player']['entry']


# def login_and_get_data(username, password):
#     with requests.Session() as client:
#         return login(client, username, password)


# def get_manager_id(csrftoken):
#     with requests.Session() as client:
#         return login_existing(client, csrftoken)


# def pick_team(csrftoken, request_payload):
#     with requests.Session() as client:
#         manager_id = login_existing(client, csrftoken)
#         client.get(PICK_TEAM_URL)
#         client.post('%s/%i/' % (PICK_TEAM_API, manager_id), json=request_payload)


# def get_player_ids(csrftoken):
#     with requests.Session() as client:
#         manager_id = login_existing(client, csrftoken)
#         return client.get('%s/%i/' % (PICK_TEAM_API, manager_id))


# def make_transfers(client2, request_payload, username, password):
#     with requests.Session() as client:
#         login(client, username, password)
#         # client.get(PICK_TEAM_URL)
#         make_transfers_response = client.post(TRANSFERS_API, json=request_payload)
#         print(make_transfers_response.url)


def get_manager_id(username, password):
    with requests.Session() as client:
        return login(client, username, password)


def pick_team(request_payload, username, password):
    with requests.Session() as client:
        manager_id = login(client, username, password)
        client.get(PICK_TEAM_URL)
        client.post('%s/%i/' % (PICK_TEAM_API, manager_id), json=request_payload)


def get_player_ids(username, password):
    with requests.Session() as client:
        manager_id = login(client, username, password)
        return client.get('%s/%i/' % (PICK_TEAM_API, manager_id))


def make_transfers(request_payload, username, password):
    with requests.Session() as client:
        login(client, username, password)
        # client.get(PICK_TEAM_URL)
        make_transfers_response = client.post(TRANSFERS_API, json=request_payload)
        print(make_transfers_response.url)
