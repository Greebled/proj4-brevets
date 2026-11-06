"""
Nose tests for acp_times.py
"""

import arrow
import acp_times
 
START = arrow.get("2017-01-01T00:00:00+00:00")
 
 
def check(control, brevet, open_hm, close_hm, start=START):
    #sssert that a control opens/closes the given (hours, minutes) after the start
    o = arrow.get(acp_times.open_time(control, brevet, start.isoformat()))
    c = arrow.get(acp_times.close_time(control, brevet, start.isoformat()))
    expected_open = start.shift(hours=open_hm[0], minutes=open_hm[1])
    expected_close = start.shift(hours=close_hm[0], minutes=close_hm[1])
    assert o == expected_open, "open {} km/{}: got {}, want {}".format(
        control, brevet, o, expected_open)
    assert c == expected_close, "close {} km/{}: got {}, want {}".format(
        control, brevet, c, expected_close)
 
 
def raises_value_error(control, brevet):
    for fn in (acp_times.open_time, acp_times.close_time):
        try:
            fn(control, brevet, START.isoformat())
        except ValueError:
            continue
        raise AssertionError("{}({}, {}) did not raise ValueError".format(
            fn.__name__, control, brevet))
 
#worked examples from the RUSA rules page
 
def test_example_1_200km():
    check(60, 200, (1, 46), (4, 0))
    check(120, 200, (3, 32), (8, 0))
    check(175, 200, (5, 9), (11, 40))
 
 
def test_example_1_finish_past_nominal():
    #205 km finish on a 200 km brevet uses the 200 km times
    check(205, 200, (5, 53), (13, 30))
 
 
def test_example_2_600km_crosses_segments():
    check(100, 600, (2, 56), (6, 40))
    check(200, 600, (5, 53), (13, 20)) #not the 200 km finish limit
    check(350, 600, (10, 34), (23, 20))
    check(550, 600, (17, 8), (36, 40))
 
 
def test_example_3_1000km():
    check(890, 1000, (29, 9), (65, 23))
 
 
#finish controls use the fixed overall limits
 
def test_finish_limits():
    check(200, 200, (5, 53), (13, 30))
    check(300, 300, (9, 0), (20, 0))
    check(400, 400, (12, 8), (27, 0))
    check(600, 600, (18, 48), (40, 0))
    check(1000, 1000, (33, 5), (75, 0))
 
 
def test_finish_up_to_20_percent_long():
    check(480, 400, (12, 8), (27, 0))
    check(240, 200, (5, 53), (13, 30))
 
 
#start and early controls
 
def test_start_control():
    #opens at the start, closes one hour later
    check(0, 200, (0, 0), (1, 0))
 
 
def test_early_controls_use_20kmh_plus_one_hour():
    #20/20 + 1 = 2h00 (plain 15 km/h would give 1h20)
    check(20, 200, (0, 35), (2, 0))
    #50/20 + 1 = 3h30 (plain 15 km/h would give 3h20)
    check(50, 300, (1, 28), (3, 30))
    #at 60 km both rules agree; past 60 km the table applies
    check(61, 200, (1, 48), (4, 4))
 
 
#dates, time zones and input types
 
def test_rollover_to_next_day():
    start = arrow.get("2017-01-01T22:00:00+00:00")
    check(200, 200, (5, 53), (13, 30), start=start)
    c = arrow.get(acp_times.close_time(200, 200, start.isoformat()))
    assert c.format("YYYY-MM-DD HH:mm") == "2017-01-02 11:30"
 
 
def test_time_zone_preserved():
    start = "2017-07-04T06:00:00-07:00"
    o = arrow.get(acp_times.open_time(100, 200, start))
    assert o.utcoffset() == arrow.get(start).utcoffset()
    assert o.format("HH:mm") == "08:56"
 
 
def test_fractional_and_string_distances():
    check(175.0, 200, (5, 9), (11, 40))
    check("175", "200", (5, 9), (11, 40))
 
 
#invalid input
 
def test_rejects_too_long_control():
    raises_value_error(241, 200)
    raises_value_error(1201, 1000)
 
 
def test_rejects_negative_control():
    raises_value_error(-1, 200)
 
 
def test_rejects_unofficial_brevet():
    raises_value_error(100, 250)
    raises_value_error(100, 1200)
 