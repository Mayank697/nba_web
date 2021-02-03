from flask import Flask
from flask import render_template

import nba_py

from datetime import datetime

app = Flask(__name__)

# routing
@app.route("/")
def index():
    render_template("index.html",
                    title="Daily Scores")


# runing main function
if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8080", threaded=True, debug=True)