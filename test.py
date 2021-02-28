from nbapy import scoreboard
from nbapy import game
import pandas as pd
import datetime
from pytz import timezone

game_id = '0021900017'  # taken from 'https://stats.nba.com/game/0021900017/'
date = datetime.datetime.today() - datetime.timedelta(1)
stats = scoreboard.Scoreboard(month=date.month, day=date.day, year=date.year)
scores = stats.line_score()
status = stats.game_header()
boxscore = game.PlayByPlay(game_id="0022000393")
available_videos = boxscore.available_video()
# for team in scores:
#     print(team)

# print("====================================================================================")

# for i in available_videos:
#     print(i)
# print(status)

print(available_videos.head())