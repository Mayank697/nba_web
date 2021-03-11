from nbapy import scoreboard
from nbapy import game
import pandas as pd
import datetime
from pytz import timezone
from constants import CITY_TO_TEAM

game_id = '0021900017'  # taken from 'https://stats.nba.com/game/0021900017/'
date = datetime.datetime.today() - datetime.timedelta(1)
stats = scoreboard.Scoreboard(month=1, day=1, year=2019)
east = stats.east_conf_standings_by_day()
team = CITY_TO_TEAM
# k = game.BoxScore("0022000536")
# j = k.players_stats()
# game_stats = game.Info("0022000536")
# game_summary = game_stats.game_summary()
# home_team = game_summary["GAMECODE"][12:16]
# print(home_team)

print(east)
# print(east[['TEAM_ID']])
# for value in east["TEAM"]:
#     print(value)
# east_stands = east.to_dict('list')
# print(east_stands)
# for value in east.index:
#     if(east["TEAM"][value] in team):
#         print(team[east["TEAM"][value]]["img"]+"------")
#         print(team[east["TEAM"][value]]["abbrev"])