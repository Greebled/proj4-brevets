"""
Open and close time calculations
for ACP-sanctioned brevets
following rules described at https://rusa.org/octime_alg.html
and https://rusa.org/pages/rulesForRiders
"""
import math
import arrow

#  Note for CIS 322 Fall 2016:
#  You MUST provide the following two functions
#  with these signatures, so that I can write
#  automated tests for grading.  You must keep
#  these signatures even if you don't use all the
#  same arguments.  Arguments are explained in the
#  javadoc comments.
#

BREVET_DISTANCES = (200, 300, 400, 600, 1000)

SPEED_TABLE = (
   (0, 200, 15, 34),
   (200, 400, 15, 32),
   (400, 600, 15, 30),
   (600, 1000, 11.428, 28),
   (1000, 1300, 13.333, 26),
)

FINAL_CLOSE = {
   200: (13, 30),
   300: (20, 0),
   400: (27, 0),
   600: (40, 0),
   1000: (75, 0),
}

MAX_OVERSHOOT = 1.2

EARLY_CONTROL_KM = 60
EARLY_CONTROL_SPEED = 20
EARLY_CONTROL_EXTRA_HOURS = 1

def _validate(control_dist_km, brevet_dist_km):
   #check arguments; return (control km, brevet km) as numbers
   #raises ValueError on anything the rules don't cover
   try:
      control = float(control_dist_km)
      brevet = int(brevet_dist_km)
   except (TypeError, ValueError):
      raise ValueError("Distances must be numbers")
   if brevet not in BREVET_DISTANCES:
      raise ValueError("Brevet distance must be one of {}".format(
         ", ".join(str(d) for d in BREVET_DISTANCES)))
   if control < 0:
      raise ValueError("Control distance cannot be negative")
   if control > brevet * MAX_OVERSHOOT:
      raise ValueError(
         "Control at {:g} km is more than 20% beyond a {} km brevet"
         .format(control, brevet))
   return control, brevet
 
 
def _hours_from_table(dist_km, which_speed):
   #sum time over each segment of the speed table up to dist_km
   #which_speed is 0 for minimum speed, 1 for maximum speed
   hours = 0.0
   for start, end, min_speed, max_speed in SPEED_TABLE:
      if dist_km <= start:
         break
      speed = (min_speed, max_speed)[which_speed]
      hours += (min(dist_km, end) - start) / speed
   return hours
 
 
def _round_minutes(hours):
   #convert hours to whole minutes, rounding halves up
   return int(math.floor(hours * 60 + 0.5))
 
 
def _shift(brevet_start_time, minutes):
   return arrow.get(brevet_start_time).shift(minutes=minutes).isoformat()


def open_time(control_dist_km, brevet_dist_km, brevet_start_time):
   """
   Args:
      control_dist_km:  number, the control distance in kilometers
      brevet_dist_km: number, the nominal distance of the brevet
         in kilometers, which must be one of 200, 300, 400, 600,
         or 1000 (the only official ACP brevet distances)
      brevet_start_time:  An ISO 8601 format date-time string indicating
         the official start time of the brevet
   Returns:
      An ISO 8601 format date string indicating the control open time.
      This will be in the same time zone as the brevet start time.
   """
   control, brevet = _validate(control_dist_km, brevet_dist_km)
   effective = min(control, brevet)
   minutes = _round_minutes(_hours_from_table(effective, 1))
   return _shift(brevet_start_time, minutes)


def close_time(control_dist_km, brevet_dist_km, brevet_start_time):
   """
   Args:
      control_dist_km:  number, the control distance in kilometers
         brevet_dist_km: number, the nominal distance of the brevet
         in kilometers, which must be one of 200, 300, 400, 600, or 1000
         (the only official ACP brevet distances)
      brevet_start_time:  An ISO 8601 format date-time string indicating
         the official start time of the brevet
   Returns:
      An ISO 8601 format date string indicating the control close time.
      This will be in the same time zone as the brevet start time.
   """
   control, brevet = _validate(control_dist_km, brevet_dist_km)
   if control >= brevet:
      #finish control: fixed overall time limit
      hours, mins = FINAL_CLOSE[brevet]
      minutes = hours * 60 + mins
   elif control <= EARLY_CONTROL_KM:
      #includes the start (0 km), which closes one hour after start
      minutes = _round_minutes(control / EARLY_CONTROL_SPEED
                              + EARLY_CONTROL_EXTRA_HOURS)
   else:
      minutes = _round_minutes(_hours_from_table(control, 0))
   return _shift(brevet_start_time, minutes)
