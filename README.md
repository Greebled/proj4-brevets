# ACP Brevet Control Times Calculator
 
A web replacement for the RUSA ACP control time calculator
(<https://rusa.org/octime_acp.html>). Enter control distances and the page
fills in each control's open and close times as you type, using Ajax calls
to a Flask server.
 
Author: Jasper Riggs, jasr@uoregon.edu
Repository: https://github.com/Greebled/proj4-brevets.git
 
## Using the calculator
 
1. Choose the brevet distance (200, 300, 400, 600 or 1000 km).
2. Set the start date and time.
3. Type each control's distance in miles or kilometers. The other unit,
   the open time and the close time fill in automatically.
Changing the brevet distance or start time recalculates every row.
Problems with a row (a distance that isn't a number, or a control too
far past the finish) appear in that row's Notes column.
 
Times are shown in the same clock as the start time you entered; no time
zone conversion is done.
 
## Control time rules
 
These are the rules from
<https://rusa.org/pages/acp-brevet-control-times-calculator>, written out
where the original is ambiguous.
 
### Speed table
 
| Control location (km) | Minimum speed (km/h) | Maximum speed (km/h) |
|-----------------------|----------------------|----------------------|
| 0 – 200               | 15                   | 34                   |
| 200 – 400             | 15                   | 32                   |
| 400 – 600             | 15                   | 30                   |
| 600 – 1000            | 11.428               | 28                   |
| 1000 – 1300           | 13.333               | 26                   |
 
### Opening time
 
The opening time is the time needed to ride to the control at the
maximum speed. The speed changes along the route: each stretch of road
is ridden at the speed for the band it lies in. For a control at 350 km:
 
200/34 + 150/32 = 5.882 + 4.688 = 10.570 h  →  10H34
 
### Closing time
 
The closing time is the time needed at the minimum speed, worked out the
same way, band by band. For a control at 890 km:
 
600/15 + 290/11.428 = 40 + 25.377 = 65.377 h  →  65H23
 
### Rounding
 
Total hours are converted to minutes and rounded to the nearest whole
minute (halves round up). Rounding is done once, on the total, not
separately for each band.
 
### Special cases
 
- Start control (0 km): opens at the start, closes one hour later.
- Controls up to 60 km: close at distance / 20 + 1 hours, which
  gives riders more time at early controls. At 60 km this equals the
  normal 15 km/h rule (4H00), so there is no jump. Opening times are not
  affected.
- Finish control: closes at the overall time limit for the brevet,
  not the table value: 13H30 for 200 km, 20H00 for 300 km, 27H00 for
  400 km, 40H00 for 600 km and 75H00 for 1000 km. A control at 200 km on
  a 600 km brevet is not a finish and closes at 13H20.
- Finish past the nominal distance: routes are often a little long. A
  control may be up to 20% past the brevet distance; it gets the same
  open and close times as a control at exactly the brevet distance
  (205 km on a 200 km brevet: 5H53 / 13H30).
- Rejected input: a negative distance, a control more than 20% past
  the brevet distance, or a brevet distance other than the five official
  ones raises ValueError in acp_times.py, and the page shows the
  message in the Notes column.
## For developers
 
### Layout
 
| File | Purpose |
|------|---------|
| `acp_times.py` | `open_time` and `close_time`: all the rules above |
| `flask_brevets.py` | Flask app; serves the page and the `/_calc_times` endpoint |
| `config.py`, `credentials.ini` | Configuration (port, secret key, debug) |
| `templates/calc.html` | The page and its JavaScript |
| `test_acp_times.py` | Nose test suite |
 
### acp_times API
 
open_time(control_dist_km, brevet_dist_km, brevet_start_time) -> str
close_time(control_dist_km, brevet_dist_km, brevet_start_time) -> str

 
brevet_start_time is an ISO 8601 string (or an Arrow object). The result
is an ISO 8601 string in the same time zone.
 
### /_calc_times endpoint
 
GET /_calc_times?km=175&brevet_dist_km=200&begin_date=2017-01-01&begin_time=00:00
 
Returns {"result": {"open": ..., "close": ..., "note": ...}}, or
{"error": "message"} if the input can't be used.
 
### Running
 
Fill in credentials.ini (author, repo, port, and a real SECRET_KEY,
for example the output of python -c "import os; print(os.urandom(24).hex())").
 
Locally:
 
pip install -r requirements.txt
python flask_brevets.py        # add -D for debug logging
 
With Docker:
 
docker build -t brevets .
docker run -d -p 5000:5000 brevets
 
Then open <http://localhost:5000>.
 
### Testing
 
From this directory:
 
    nosetests
 
The tests cover the worked examples from the RUSA rules page, every finish
limit, the start control, the 60 km rule, routes up to 20% long, day
rollover, time zones, and rejected input. Expected values were checked
against the RUSA calculator.
 
Note: nose does not work on Python 3.10 or newer. Use Python 3.9 (as the
Dockerfile does), or run the tests inside the container:
 
    docker run --rm --entrypoint nosetests brevets