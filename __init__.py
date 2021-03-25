from flask import Flask
from flask import render_template
from flask import request
from flask import url_for, redirect, session
from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired
from wtforms import validators, SubmitField

from nbapy import scoreboard 
from constants import CITY_TO_TEAM
from constants import TEAM_ID_DATA

from datetime import datetime, timedelta

import collections
import praw
import pytz
import requests
import time
import dateutil.parser

import nbapy
from nbapy.constants import CURRENT_SEASON
from nbapy.constants import TEAMS
from constants import CITY_TO_TEAM

from nbapy import constants 
from nbapy import game
from nbapy import player
from nbapy import team  
from nbapy import league
from nbapy import draft_combine


from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.tools import argparser


from bs4 import BeautifulSoup
from werkzeug.utils import redirect

# YouTube Developer Key
DEVELOPER_KEY = ""
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


app = Flask(__name__)
app = Flask(__name__, static_url_path='/static')

app.config['SECRET_KEY'] = '#$%^&*'

class InfoForm(FlaskForm):
    date = DateField('date', format='%Y-%m-%d', validators=(validators.DataRequired(),))
    submit = SubmitField('Submit')

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
        boxscore_summary = game.Info(gameid)
    except:
        return render_template("boxscores.html",title="boxscore,len_team_stats=0")


    boxscore_game_summary = boxscore_summary.game_summary()
    for value in boxscore_game_summary.index:
        home_team = boxscore_game_summary["GAMECODE"][value][9:12]
        away_team = boxscore_game_summary["GAMECODE"][value][12:16]

    if home_team in TEAM_ID_DATA:
         home_team_city = TEAM_ID_DATA[home_team]["city"]
         home_team_name = TEAM_ID_DATA[home_team]["name"]
         home_team_logo = TEAM_ID_DATA[home_team]["img"]
    else:
         home_team_logo = False

    if away_team in TEAM_ID_DATA:
         away_team_city = TEAM_ID_DATA[away_team]["city"]
         away_team_name = TEAM_ID_DATA[away_team]["name"]
         away_team_logo = TEAM_ID_DATA[away_team]["img"]
    else:
         away_team_logo = False

    for value in boxscore_game_summary.index:
        boxscore_game_date = boxscore_game_summary["GAME_DATE_EST"][value]
    
    datetime_boxscore = datetime.strptime(boxscore_game_date[:10], "%Y-%m-%d")
    pretty_date = datetime_boxscore.strftime("%b %d, %y")

    #get current season like "2020-2021"
    for value in boxscore_game_summary.index:
        to_year = int(boxscore_game_summary["SEASON"][value])
    next_year = to_year + 1

    season = str(to_year) + "-" + str(next_year)[2:4]

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
    for i in team_stats.index:
        if i in team_stats:
            leading_points = team_stats["PTS"][i]
            winning = team_stats["TEAM_ABBREVIATION"][i]
        elif team_stats["PTS"][i] < leading_points:
            continue
        else:
            winning = False
    # Add a 0 to a single digit minute like 4:20 to 04:20
    # Because bootstrap-datatable requires consistency.                          
    for i in player_stats.index:
        if (player_stats["MIN"][i] and not isinstance(player_stats["MIN"][i], int)):
            if (len(player_stats["MIN"][i]) == 4):
                player_stats["MIN"][i] = "0" + player_stats["MIN"][i]


    if (len_team_stats !=0):
        team_summary_info = [team.TeamSummary(team_stats["TEAM_ID"][0],season=season).info(),team.TeamSummary(team_stats["TEAM_ID"][1],season=season).info()]

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
    # post_game_thread = get_post_game_thread(next_year, boxscore_game_summary[0]["GAME_STATUS_TEXT"],boxscore_line_score, team_stats)

    #Get link for fullmatchtv (full broadcast video link). It takes 2 extra seconds.
    full_match_url = False
    

    if ((next_year > 2016) and (boxscore_game_summary["GAME_STATUS_TEXT"][0] == "Final")):
        match_date = datetime_boxscore.strftime("%b-%d-%Y")
        full_match_url = search_nba_full_match(away_team_city,
                                               away_team_name,
                                               home_team_city,
                                               home_team_name,
                                               match_date)
    else:
        full_match_url = False
    

    if (not team_stats.empty and boxscore_game_summary["GAME_STATUS_TEXT"][0] == "Final"):
        youtube_search_query = team_stats["TEAM_CITY"][0] + " " + \
                               team_stats["TEAM_NAME"][0] + " vs " + \
                               team_stats["TEAM_CITY"][1] + " " + \
                               team_stats["TEAM_NAME"][1] + " " + \
                               pretty_date
        youtube_url = youtube_search(youtube_search_query, 1)
    else:
        youtube_url = False

    inactive_players = boxscore_summary.inactive_players()
    officials = boxscore_summary.officials()

    return render_template("boxscores.html",title="boxscore",
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

def search_nba_full_match(away_team_city,
                          away_team_name,
                          home_team_city,
                          home_team_name,
                          match_date):
    """Searches for nba full game recording from fullmatchtv.com
    """
    link_version_one = "http://fullmatchtv.com/nba/"
    link_version_two = "http://fullmatchtv.com/nba/"

    split_away_team_city = away_team_city.split()
    split_home_team_city = home_team_city.split()

    for i in split_away_team_city:
        link_version_one += i + "-"
    link_version_one += away_team_name + "-"

    for i in split_home_team_city:
        link_version_one += i + "-"
        link_version_two += i + "-"
    link_version_one += home_team_name + "-"
    link_version_two += home_team_name + "-"

    for i in split_away_team_city:
        link_version_two += i + "-"
    link_version_two += away_team_name + "-"

    link_version_one += match_date
    link_version_two += match_date

    if (test_link(link_version_one)):
        return link_version_one 
    elif (test_link(link_version_two)):
        return link_version_two
    else:
        return False

def youtube_search(q, max_results=25, freedawkins=None):
    """Searches YouTube for q and returns YouTube link.
    """
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    # Call the search.list method to retrieve results matching the specified
    # query term.
    if (freedawkins):
        search_response = youtube.search().list(q=q,
                                                part="id,snippet",
                                                maxResults=max_results,
                                                channelId="UCEjOSbbaOfgnfRODEEMYlCw").execute()
    else:
        search_response = youtube.search().list(q=q,
                                                part="id,snippet",
                                                maxResults=max_results,
                                                type="video").execute()

    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            return "//www.youtube.com/embed/" + search_result["id"]["videoId"]

    return False



@app.route('/standings')
def standings():
    '''
        Default Standings
    '''
    stats = scoreboard.Scoreboard()
    east_standings = stats.east_conf_standings_by_day()
    west_standings = stats.west_conf_standings_by_day()

    return render_template("standings.html",
                            title="standings",
                            east_standings=east_standings,
                            west_standings=west_standings,
                            team=CITY_TO_TEAM)

@app.route('/standings/season/<season>')
def standings_by_season(season):
    """Standings page by the season year
    """
    season = int(season)+1
    stats = scoreboard.Scoreboard(month=7, day=1, year=season)
    east_standings = stats.east_conf_standings_by_day()
    west_standings = stats.west_conf_standings_by_day()

    return render_template('standings.html',
                            title='standings',
                            east_standings=east_standings,
                            west_standings=west_standings,
                            team=CITY_TO_TEAM)

@app.route('/standings', methods=['POST'])
def standings_post_request():
    """
    Standings page after using the datepicker plugin
    """
    date = request.form["date"]
    datetime_object = datetime.strptime(date, "%m-%d-%Y")
    stats = scoreboard.Scoreboard(month=datetime_object.month, day=datetime_object.day, year=datetime_object.year)
    east_standings = stats.east_conf_standings_by_day()
    west_standings = stats.west_conf_standings_by_day()

    return render_template('standings.html',
                            title='standings',
                            east_standings=east_standings,
                            west_standings=west_standings,
                            team=CITY_TO_TEAM)

@app.route('/teams/<teamid>')
def teams(teamid):
    '''Specific team pages.
    '''
    team_summary = team.TeamSummary(teamid)
    team_summary_info = team_summary.info()
    team_season_ranks = team_summary.season_ranks()

    team_common_roaster = team.CommonRoster(teamid)
    coaches = team_common_roaster.coaches()
    roaster = team_common_roaster.roster()
    
    season = team_summary_info["SEASON_YEAR"][0]

    team_game_log = team.GameLogs(teamid, season=season)
    team_games = team_game_log.logs()

    playoff_game_logs = team.GameLogs(teamid, season_type='Regular Season')
    playoff_team_games = playoff_game_logs.logs()

    team_season = team.SeasonResults(teamid)
    team_season_result = team_season.results()

    for k in team_season_result.index:
        if(team_season_result["YEAR"][k] == season):
            current_season_info = k

    return render_template("teams.html",
                            title=team_summary_info["TEAM_CITY"][0] + " " + team_summary_info["TEAM_NAME"][0],
                            temaid=teamid,
                            team_summary_info=team_summary_info,
                            team_season_ranks=team_season_ranks,
                            season=season,
                            team_games=team_games,
                            playoff_team_games=playoff_team_games,
                            team_season=team_season_result,
                            roaster=roaster,
                            coaches=coaches,
                            current_season_info=current_season_info,
                            team_img=TEAM_ID_DATA)

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