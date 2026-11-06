"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config

import logging

###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY

###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############

def _parse_start(begin_date, begin_time):
    """Combine the form's date and time fields into an Arrow object.
    Browsers send the time as HH:mm, or HH:mm:ss if seconds are shown.
    The time is taken as given, with no time zone conversion.
    """
    for fmt in ("YYYY-MM-DD HH:mm", "YYYY-MM-DD HH:mm:ss"):
        try:
            return arrow.get("{} {}".format(begin_date, begin_time), fmt)
        except ValueError:  # arrow.ParserError is a ValueError
            continue
    raise ValueError("Start date/time is not valid")

@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("request.args: {}".format(request.args))
    km = request.args.get('km', None, type=float)
    brevet_dist_km = request.args.get('brevet_dist_km', 200, type=int)
    begin_date = request.args.get('begin_date', '')
    begin_time = request.args.get('begin_time', '')
 
    if km is None:
        return flask.jsonify(error="Distance must be a number")
    try:
        start = _parse_start(begin_date, begin_time).isoformat()
        open_time = acp_times.open_time(km, brevet_dist_km, start)
        close_time = acp_times.close_time(km, brevet_dist_km, start)
    except ValueError as err:
        app.logger.debug("Rejected request: {}".format(err))
        return flask.jsonify(error=str(err))
 
    note = ""
    if km > brevet_dist_km:
        note = "Past {} km; finish times apply".format(brevet_dist_km)
    result = {"open": open_time, "close": close_time, "note": note}
    return flask.jsonify(result=result)


#############

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
