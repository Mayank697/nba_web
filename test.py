from nbapy import scoreboard
from nbapy import game
import pandas as pd
import datetime
from pytz import timezone

game_id = '0021900017'  # taken from 'https://stats.nba.com/game/0021900017/'
date = datetime.datetime.today() - datetime.timedelta(1)
stats = scoreboard.Scoreboard(month=date.month, day=date.day, year=date.year)
east = stats.east_conf_standings_by_day()
k = game.BoxScore("0022000536")
j = k.players_stats()
summary = game.
# for i in east:
#     print(i["TEAM"])
for i in j:
    print(i)
# scores = stats.line_score()
# status = stats.game_header()
# boxscore = game.PlayByPlay(game_id="0022000393")
# available_videos = boxscore.available_video()
# for team in scores:
#     print(team)

east_standing = stats.east_conf_standings_by_day()
series_standing = stats.series_standings()
for i in series_standing:
    print(i)
# print(east_standing.head())
# print(series_standing.head())
# scores = stats.line_score()
# status = stats.game_header()
# boxscore = game.PlayByPlay(game_id="0022000393")
# available_videos = boxscore.available_video()
# # for team in scores:
# #     print(team)

# # print("====================================================================================")

# # for i in available_videos:
# #     print(i)
# # print(status)

# print(available_videos.head())