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
# print(team_stats)
# players_stat = boxscore.players_stats()
# print(players_stat)
# boxscore_summary = game.Info("0022000571")
# boxscore_game_summary = boxscore_summary.game_summary()
# for value in boxscore_game_summary.index:
#         boxscore_game_date = boxscore_game_summary["GAME_DATE_EST"][value]
# datetime_boxscore = datetime.datetime.strptime(boxscore_game_date[:10], "%Y-%m-%d")
# match_date = datetime_boxscore.strftime("%d-%m-%Y")
# print(match_date)
# for value in boxscore_game_summary.index:
#     print(boxscore_game_summary['GAME_DATE_EST'][value])
# for i in team_stats.index:
#     print(team_stats['PTS'][i])

# print(winning)

team_summary = team.TeamSummary("1610612751")
team_summary_info = team_summary.info()

season = team_summary_info["SEASON_YEAR"][0]

team_seasons = team.SeasonResults("1610612751", season_type="Regular Season")
seasons = team_seasons.results()
# tsr = team_summary.season_ranks()
# print(seasons)

for k in seasons.index:
        if(seasons["YEAR"][k] == season):
                current_season = k

print(k)