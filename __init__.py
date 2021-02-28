from flask import Flask
from flask import render_template
from flask import request
from flask import url_for

from nbapy import scoreboard 

from datetime import datetime, timedelta

import dateutil.parser
import requests

app = Flask(__name__)
app = Flask(__name__, static_url_path='/static')

# routing
@app.route("/")
def index():
    """
    Render's today's game on index page

    """
    datetime_today = datetime.today() - timedelta(1)
    pretty_date_today = datetime_today.strftime("%b %d, %Y")
    return render_score_page("index.html", pretty_date_today, "Daily Score")

@app.route('/scores/<datestring>')
def scores(datestring):
    """Link for specific score pages for a certain day.
    """
    return render_score_page("index.html", datestring, "Daily Score/ "+datestring)

app.route('/scores', methods=["POST"])
def scores_post_request():
    '''
        Score page after using datepicker plugin
    '''
    date = request.form["date"]
    return render_score_page("index.html", date, date)

def render_score_page(page, datestring, title):
    '''
        Args:
            page: Name of the html template to render
            datestring: date of the scoreboard
    '''
    datetime_today = dateutil.parser.parse(datestring)
    yesterday = datetime_today - timedelta(1)
    tomorrow = datetime_today + timedelta(1)
    pretty_date_today = datetime_today.strftime("%b %d, %Y")
    games = get_games(datetime_today)

    winners = []

    for i in games:
        if(i["TEAM_1_PTS"] or i["TEAM_1_PTS"]):
            if(i["TEAM_1_PTS"] > i["TEAM_2_PTS"]):
                winners.append(i["TEAM_1_ABBREVIATION"])
            elif(i["TEAM_1_PTS"] < i["TEAM_2_PTS"]):
                winners.append(i["TEAM_1_ABBREVIATION"])
            else:
                winners.append(None)
        else:
            winners.append(None)

    return render_template(page,
                            title=title,
                            pretty_date_today=pretty_date_today,
                            yesterday=yesterday,
                            tomorrow=tomorrow,
                            games=games,
                            winners=winners)



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
    game_status = stats.game_header()

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

            for status in game_status.index:
                if(line_score["GAME_ID"][team] == game_status["GAME_ID"][status]):
                    current_game["GAME_STATUS_TEXT"] = game_status["GAME_STATUS_TEXT"][status]
                    # current_game["NATL_TV_BROADCASTER_ABBREVIATION"] = game_status["NATL_TV_BROADCASTER_ABBREVIATION"][status]

            games.append(current_game.copy())
            current_game = {}
            game_sequence_counter = 0

    return games

# def get_winning_team(date):
    


# runing main function
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, threaded=True, debug=True)