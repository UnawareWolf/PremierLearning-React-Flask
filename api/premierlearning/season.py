import json
import csv
import random
import os

from abc import ABC, abstractmethod

from .player import Player
from .team import Team

FANTASY_JSON_FILE_LOCATION = 'data/season_20_21/fantasy.json'
FIXTURES_JSON_FILE_LOCATION = 'data/season_20_21/fixtures.json'
PLAYER_JSON_FILE_LOCATION = 'data/season_20_21/players/player_%i.json'
PAST_SEASON_TEAMS_CSV_LOCATION = 'data/season_%i_%i/teams.csv'
PAST_SEASON_FIXTURES_CSV_LOCATION = 'data/season_%i_%i/fixtures.csv'
PAST_SEASON_PLAYERS_DIR = 'data/season_%i_%i/players'
PAST_SEASON_ELEMENTS_FILE = 'data/season_%i_%i/players_raw.csv'
PAST_SEASON_RAW_DATA_LOCATION = 'data/season_%i_%i/raw.json'
LAST_SEASON_TEAM_STANDINGS_LOCATION = 'data/season_%i_%i/last_season_team_standings.json'


class Season(ABC):

    def __init__(self):
        self.years = ()
        self.teams = {}
        self.players = []
        self.fixtures_json = None
        self.element_type_dict = {}
        self.last_season_team_standings = None
        self.player_code_dict = {}
        self.next_gameweek = 0
        self.current_gameweek = 0

    def set_up_season(self):
        self.populate_last_season_team_standings()
        self.set_up_element_type_dict()
        self.populate_fixtures_json()
        self.populate_teams()
        self.populate_players()
        self.populate_player_code_dict()

    def set_up_element_type_dict(self):
        self.element_type_dict = self.read_json(FANTASY_JSON_FILE_LOCATION)['element_types']

    # def calculate_player_points_over_next_5_weeks(self):
    #     for player in self.players:
    #         player.calculate_points_over_next_5_weeks()
    #     self.players.sort(key=lambda player_to_sort: player_to_sort.points_over_next_5_weeks, reverse=True)

    def calculate_player_points_over_next_5_gameweeks(self):
        for player in self.players:
            player.calculate_points_over_next_5_gameweeks()
        self.players.sort(key=lambda player_to_sort: player_to_sort.points_over_next_5_gameweeks, reverse=True)

    def populate_last_season_team_standings(self):
        self.last_season_team_standings = self.read_json(LAST_SEASON_TEAM_STANDINGS_LOCATION % self.years)

    def populate_player_code_dict(self):
        for player in self.players:
            self.player_code_dict[player.code] = player

    @abstractmethod
    def populate_fixtures_json(self):
        pass

    @abstractmethod
    def populate_players(self):
        pass

    @abstractmethod
    def populate_teams(self):
        pass

    @staticmethod
    def read_json(file_path):
        with open(file_path) as file:
            return json.load(file)


class CurrentSeason(Season):

    def __init__(self):
        super().__init__()

        self.fantasy_json = None
        self.years = (20, 21)
        self.set_up_season()

    def populate_fixtures_json(self):
        self.fixtures_json = self.read_json(FIXTURES_JSON_FILE_LOCATION)

    def populate_players(self):
        for element in self.fantasy_json['elements']:
            player_file_path = PLAYER_JSON_FILE_LOCATION % element['id']
            player_json = self.read_json(player_file_path)
            self.players.append(Player(self.fantasy_json, element, player_json, self.teams, self.current_gameweek))
        random.shuffle(self.players)

    def populate_teams(self):
        self.fantasy_json = self.read_json(FANTASY_JSON_FILE_LOCATION)
        self.next_gameweek = next(event['id'] for event in self.fantasy_json['events'] if event['is_next'])
        self.current_gameweek = next(event['id'] for event in self.fantasy_json['events'] if event['is_current'])

        for team_dict in self.fantasy_json['teams']:
            team = Team(team_dict, self.fixtures_json, self.last_season_team_standings)
            self.teams[team.id] = team


class PastSeason(Season):

    def __init__(self, year_from):
        super().__init__()
        self.years = (year_from, year_from + 1)
        self.set_up_season()

    def populate_fixtures_json(self):
        self.fixtures_json = self.read_csv(PAST_SEASON_FIXTURES_CSV_LOCATION % self.years)

    def populate_players(self):
        elements = self.read_csv(PAST_SEASON_ELEMENTS_FILE % self.years)
        elements_dict = {}
        for element in elements:
            elements_dict[int(element['id'])] = element

        player_dir_list = os.listdir(PAST_SEASON_PLAYERS_DIR % self.years)
        for player_dir in player_dir_list:
            player_gameweeks = self.read_csv(PAST_SEASON_PLAYERS_DIR % self.years + '/' + player_dir + '/gw.csv')
            player_id = int(player_dir.split('_')[-1])
            player_json = {'history': player_gameweeks, 'fixtures': []}
            self.players.append(Player(None, elements_dict[player_id], player_json, self.teams, self.current_gameweek))

    def populate_teams(self):
        if self.years[0] == 18:
            raw_json = self.read_json(PAST_SEASON_RAW_DATA_LOCATION % self.years)
            teams_dict = raw_json['teams']
        else:
            teams_dict = self.read_csv(PAST_SEASON_TEAMS_CSV_LOCATION % self.years)

        for team_dict in teams_dict:
            team_dict['id'] = int(team_dict['id'])
            team = Team(team_dict, self.fixtures_json, self.last_season_team_standings)
            self.teams[team.id] = team

    @staticmethod
    def read_csv(file_path):
        with open(file_path, newline='', encoding='utf8') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            return list(csv_reader)
