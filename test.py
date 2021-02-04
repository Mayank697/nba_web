from nbapy import scoreboard
import pandas as pd

game_id = '0021900017'  # taken from 'https://stats.nba.com/game/0021900017/'
stats = scoreboard.Scoreboard(month=7, day=27, year=2020, league_id='00', offset=0)
scores = stats.line_score()
for team in scores:
    print(team)