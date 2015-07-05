import sys
import time
from datetime import datetime, timedelta
from location import Trip, Location


def convertTime(time):
    unix_basetime = 25569.0 # 01/01/1970
    unix_time = int((time - unix_basetime) * 86400);
    return unix_time


class PltTripLoader:
  @staticmethod
  def get_all_trips(trips_filename):
    trips = []
    with open(trips_filename) as f:
      f.readline()
      f.readline()
      f.readline()
      f.readline()
      f.readline()
      number = f.readline()
      for id, line in enumerate(f):
        lat, lon, started, alt, time = map(lambda x: x.strip(), line.split(','))
        time = convertTime(float(time))
        if started == "1":
          trip = Trip()
          trips.append(trip)
          prev_location = None
        next_location = Location(id, float(lat), float(lon), time)
        if prev_location:
          prev_location.next_location_id = next_location.id
          next_location.prev_location_id = prev_location.id
        trip.add_location(next_location)
        prev_location = next_location
    return trips

    
if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "Usage: %s <filename.plt>" % sys.argv[0]
    sys.exit(0)
  else:
    filename = sys.argv[1]
    PltTripLoader.get_all_trips(sys.argv[1])
  
