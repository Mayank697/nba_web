from flask import Flask
from flask import render_template

from nbapy import scoreboard 

from datetime import datetime

app = Flask(__name__)

# routing
@app.route("/")
def index():
    """
    Render's today's game on index page

    """
    datetime_today = datetime.today()
    pretty_date_today = datetime_today.strftime("%b %d, %Y")
    games = get_games(datetime_today)
    return render_template("index.html",
                           title="Daily Scores",
                           pretty_date_today=pretty_date_today,
                           games=games)

def get_games(date):
    """
    Get list of game of a day

    Args:
        date:- datetime object of the day we want games.
    
    Return:
        games:- array of dictioneries of game played on given day
    """
    stats = scoreboard.Scoreboard(month=date.month, day=date.day, year=date.year)
    line_score = stats.line_score()

    #list of games
    games = []
    #dictionary of game we're looking for
    current_game = {}

    current_game_sequence = 0
    game_sequence_counter = 0

    for team in line_score.index:
        if(line_score["GAME_SEQUENCE"][team] != current_game_sequence):
            current_game["TEAM_1_ABBREVIATION"] = line_score["TEAM_ABBREVIATION"][team]
            current_game["TEAM_1_WINS_LOSSES"] = line_score["TEAM_WINS_LOSSES"][team]
            current_game["TEAM_1_PTS"] = line_score["PTS"][team]
            current_game["TEAM_1_ID"] = line_score["TEAM_ID"][team]
            
            current_game_sequence = line_score["GAME_SEQUENCE"][team]
            game_sequence_counter += 1
        
        elif(game_sequence_counter == 1):
            current_game["TEAM_2_ABBREVIATION"] = line_score["TEAM_ABBREVIATION"][team]
            current_game["TEAM_2_WINS_LOSSES"] = line_score["TEAM_WINS_LOSSES"][team]
            current_game["TEAM_2_PTS"] = line_score["PTS"][team]
            current_game["TEAM_2_ID"] = line_score["TEAM_ID"][team]

            current_game["GAME_ID"] = line_score["GAME_ID"][team]

            games.append(current_game.copy())
            current_game = {}
            game_sequence_counter = 0

    return games

# runing main function
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, threaded=True, debug=True)