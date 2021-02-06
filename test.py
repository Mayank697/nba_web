from nbapy import scoreboard
import pandas as pd
import datetime
from pytz import timezone

game_id = '0021900017'  # taken from 'https://stats.nba.com/game/0021900017/'
date = datetime.datetime.today() - datetime.timedelta(1)
stats = scoreboard.Scoreboard(month=date.month, day=date.day, year=date.year)
scores = stats.line_score()
status = stats.game_header()
# for team in scores:
#     print(team)

# print("====================================================================================")

for i in status:
    print(i)
# print(status)