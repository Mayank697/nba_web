from flask import Flask
from flask import render_template
from flask import request
from flask import url_for

from nbapy import scoreboard 
from constants import CITY_TO_TEAM
from constants import TEAM_ID_DATA

from datetime import datetime, timedelta

import dateutil.parser
import requests
import nbapy
from nbapy.constants import CURRENT_SEASON
from nbapy.constants import TEAMS
from nbapy import constants 
from nbapy import game
from nbapy import player
from nbapy import team  
from nbapy import league
from nbapy import draft_combine

from constants import CITY_TO_TEAM

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
    return render_score_page("index.html", pretty_date_today, "NBA-Stats")

@app.route('/scores/<datestring>')
def scores(datestring):
    """Link for specific score pages for a certain day.
    """
    return render_score_page("index.html", datestring, "NBA-Stats")

@app.route('/scores', methods=["POST"])
def scores_post_request():
    '''
        Score page after using datepicker plugin
    '''
    date = request.form["date"]
    return render_score_page("index.html", date, "NBA-Stats")

@app.route('/boxscores/<gameid>')
def boxscore(gameid, season=CURRENT_SEASON):
    boxscore = game.BoxScore(gameid)

    player_stats = boxscore.players_stats()
    team_stats = boxscore.team_stats()

    len_player_stats = len(player_stats)
    len_team_stats = len(team_stats)
    num_starters = 5
    starters_title = True

    try:
        boxscore_summary = game.BoxscoreSummary(gameid)
    except:
        return render_template("boxscores.html",title="boxscore,len_team_stats=0")


    boxscore_game_summary = boxscore_summary.game_summary()
    home_team = boxscore_game_summary[0]["GAMECODE"][9:12]
    away_team = boxscore_game_summary[0]["GAMECODE"][12:16]

    if home_team in TEAM_ID_DATA:
         home_team_city = TEAM_ID_DATA[home_team]["city"]
         home_team_city = TEAM_ID_DATA[home_team]["name"]
         home_team_city = TEAM_ID_DATA[home_team]["img"]
    else:
         home_team_logo = False

    if away_team in TEAM_ID_DATA:
         away_team_city = TEAM_ID_DATA[away_team]["city"]
         away_team_city = TEAM_ID_DATA[away_team]["img"]
         away_team_city = TEAM_ID_DATA[away_team]["name"]
    else:
         away_team_logo = False

    boxscore_game_date = boxscore_game_summary[0]["GAME_DATE_EST"]
    datetime_boxscore = datetime.datetime.strptime(boxscore_game_date[:10], "%y-%m-%d")
    pretty_date = datetime_boxscore.strftime("%b %d, %y")

       #get current season like "2016-17"
    to_year = int(boxscore_game_summary[0]["SEASON"])
    next_year = to_year + 1

    season = str(to_year) + "_" + str(next_year)[2:4]

       #Create NBA recap link
    recap_date = datetime_boxscore.strftime("%Y/%m/%d") 
      # Get nba recap video links for previous years like 2016 or before.
       # It takes 2 extra seconds. Commenting for now.
     # nba_recap = False
    if(to_year < 2016):
        nba_recap = "http://www.nba.com/video/" + recap_date + "/" + gameid + "-" + home_team + "-" + away_team + "-recap"
        if not test_link(nba_recap):
            yesterday = datetime_boxscore - datetime.timedelta(1)
            recap_date = yesterday.strftime("%Y/%m/%d")
            nba_recap = "http://www.nba.com/video/" + recap_date + "/" + gameid + "-" + home_team + "-" + away_team + "-recap"
            if not test_link(nba_recap):
                nba_recap = False
    else:
        nba_recap = False

    #Figure out which team won or is winning.
    leading_points = 0
    winning = ""
    for i in team_stats:
        if i in team_stats:
            leading_points = i["PTS"]
            winning = I["TEAM_ABBREVIATION"]
        elif i["PTS"] < leading_points:
            continue
        else:
            winning = False
    # Add a 0 to a single digit minute like 4:20 to 04:20
    # Because bootstrap-datatable requires consistency.                          
    for i in player_stats:
        if (i["MIN"] and not isinstance(i["MIN"], int)):
            if (len(i["MIN"]) == 4):
                i["MIN"] = "0" + i["MIN"]


    if (len_team_stats !=0):
        team_summary_info = [team.TeamSummary(team_stats[0]["TEAM_ID"],season=season).info(),team.TeamSummary(team_stats[1]["TEAM_ID"],season=season).info()]

    else:
        team_summary_info = False
    #Search for relevant reddit Post Game Thread.
    boxscore_line_score = boxscore_summary.line_score()
    """
    startTime = time.time()
    elapsedTime = time.time() - startTime
    elapsedTIme = elapsedTime * 1000
    print(elapsedTime)
    """
    #post_game_thread = False
    post_game_thread = get_post_game_thread(next_year, boxscore_game_summary[0]["GAME_STATUS_TEXT"],boxscore_line_score, team_stats)

    #Get link for fullmatchtv (full broadcast video link). It takes 2 extra seconds.
    full_match_url = False
    """

     if (next_year > 2016 and boxscore_game_summary[0]["GAME_STATUS_TEXT"] == "Final"):
        match_date = datetime_boxscore.strftime("%b-%-d-%Y")
        full_match_url = search_nba_full_match(away_team_city,
                                               away_team_name,
                                               home_team_city,
                                               home_team_name,
                                               match_date)
    else:
        full_match_url = False
    """

    if (team_stats and boxscore_game_summary[0]["GAME_STATUS_TEXT"] == "Final"):
        youtube_search_query = team_stats[0]["TEAM_CITY"] + " " + \
                               team_stats[0]["TEAM_NAME"] + " vs " + \
                               team_stats[1]["TEAM_CITY"] + " " + \
                               team_stats[1]["TEAM_NAME"] + " " + \
                               pretty_date
        youtube_url = youtube_search(youtube_search_query, 1)
    else:
        youtube_url = False

    inactive_players = boxscore_summary.inactive_players()
    officials = boxscore_summary.officials()

    return render_template("boxscore.html",title="boxscore",
                            player_stats=player_stats,
                            len_player_stats=len_player_stats,
                            len_team_stats=len_team_stats,
                            starters_title=starters_title,
                            num_starters=num_starters,
                            team_stats=team_stats,
                            winning=winning,
                            team_summary_info=team_summary_info,
                            pretty_date=pretty_date,
                            boxscore_line_score=boxscore_line_score,
                            post_game_thread=post_game_thread,
                            home_team=home_team,
                            away_team=away_team,
                            home_team_logo=home_team_logo,
                            away_team_logo=away_team_logo,
                            nba_recap=nba_recap,
                            full_match_url=full_match_url,
                            youtube_url=youtube_url,
                            inactive_players=inactive_players,
                            officials=officials)
def test_link(link):
    """Test if link is valid.
    """
    r = requests.get(link)
    if (r.status_code != 200):
        return False
    else:
        return True
                                    





         




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
        if(i["TEAM_1_PTS"] or i["TEAM_2_PTS"]):
            if(i["TEAM_1_PTS"] > i["TEAM_2_PTS"]):
                winners.append(i["TEAM_1_ABBREVIATION"])
            elif(i["TEAM_1_PTS"] < i["TEAM_2_PTS"]):
                winners.append(i["TEAM_2_ABBREVIATION"])
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