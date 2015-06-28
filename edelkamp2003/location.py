#
# Location-related classes for simplification of GPS traces.
# Author: James P. Biagioni (jbiagi1@uic.edu)
# Company: University of Illinois at Chicago
# Created: 5/16/11
#

import os

class Location:
    def __init__(self, id, latitude, longitude, time):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.orig_latitude = latitude
        self.orig_longitude = longitude
        self.time = time
        self.prev_location = None
        self.next_location = None
    
    def __str__(self):
        location_string = str(self.id) + "," + str(self.latitude) + "," + str(self.longitude) + "," + str(self.time)
        
        if (self.prev_location is not None):
            location_string += "," + str(self.prev_location.id)
        else:
            location_string += ",None"
        
        if (self.next_location is not None):
            location_string += "," + str(self.next_location.id)
        else:
            location_string += ",None"
        
        return location_string

class Trip:
    def __init__(self):
        self.locations = []
    
    def add_location(self, bus_location):
        self.locations.append(bus_location)
    
    @property
    def num_locations(self):
        return len(self.locations)
    
    @property
    def start_time(self):
        return self.locations[0].time
    
    @property
    def end_time(self):
        return self.locations[-1].time
    
    @property
    def time_span(self):
        return (self.locations[-1].time - self.locations[0].time)

class TripLoader:
    
    @staticmethod
    def get_all_trips(trips_path):
        
        # storage for all trips
        all_trips = []
        
        # get trip filenames
        trip_filenames = os.listdir(trips_path)
        
        # iterate through all trip filenames
        for trip_filename in trip_filenames:
            
            # if filename starts with "trip_"
            if (trip_filename.startswith("trip_") is True):
                
                # load trip from file
                curr_trip = TripLoader.load_trip_from_file(trips_path + trip_filename)
                
                # add trip to all_trips list
                all_trips.append(curr_trip)
        
        # return all trips
        return all_trips
    
    @staticmethod
    def load_trip_from_file(trip_filename):
        
        # create new trip object
        new_trip = Trip()
        
        # create new trip locations dictionary
        new_trip_locations = {} # indexed by location id
        
        # open trip file
        trip_file = open(trip_filename, 'r')
        
        # read through trip file, a line at a time
        for trip_location in trip_file:
            
            # parse out location elements
            location_elements = trip_location.strip('\n').split(',')
            
            # create new location object
            new_location = Location(str(location_elements[0]), float(location_elements[1]), float(location_elements[2]), float(location_elements[3]))
            
            # store new trip location
            new_trip_locations[new_location.id] = new_location
            
            # store prev/next_location id
            new_location.prev_location_id = str(location_elements[4])
            new_location.next_location_id = str(location_elements[5])
            
            # add new location to trip
            new_trip.add_location(new_location)
        
        # close trip file
        trip_file.close()
        
        # iterate through trip locations, and connect pointers
        for trip_location in new_trip.locations:
            
            # connect prev_location pointer
            if (trip_location.prev_location_id != "None"):
                trip_location.prev_location = new_trip_locations[trip_location.prev_location_id]
            else:
                trip_location.prev_location = None
            
            # connect next_location pointer
            if (trip_location.next_location_id != "None"):
                trip_location.next_location = new_trip_locations[trip_location.next_location_id]
            else:
                trip_location.next_location = None
        
        # return new trip
        return new_trip
