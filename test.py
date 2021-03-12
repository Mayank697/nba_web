from nbapy import scoreboard
from nbapy import game
from nbapy import team
import pandas as pd
import datetime
from pytz import timezone
from constants import CITY_TO_TEAM

game_id = '0021900017'  # taken from 'https://stats.nba.com/game/0021900017/'
date = datetime.datetime.today() - datetime.timedelta(1)
# stats = scoreboard.Scoreboard()
boxscore = game.BoxScore("0022000536")
team_stats = boxscore.team_stats()
print(team_stats)
# players_stat = boxscore.players_stats()
# print(players_stat)
boxscore_summary = game.Info("0022000536")
boxscore_game_summary = boxscore_summary.game_summary()
# for value in boxscore_game_summary.index:
#     print(boxscore_game_summary['GAME_DATE_EST'][value])
# for i in team_stats.index:
#     print(team_stats['PTS'][i])

# print(winning)