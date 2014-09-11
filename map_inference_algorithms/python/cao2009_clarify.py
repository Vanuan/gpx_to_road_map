#
# Implementation of the "Clarification" algorithm.
# Author: James P. Biagioni (jbiagi1@uic.edu)
# Company: University of Illinois at Chicago
# Created: 6/9/11
#

import time
import math
import sys
import os
from pylibs import spatialfunclib, mathfunclib
from rtree import Rtree
from location import TripLoader

all_trips = TripLoader.get_all_trips("trips/")

# global parameters
force_step = 1.0
spring_force_constant = 0.005
attraction_force_sigma = 5.0
trip_max=len(all_trips)

class Edge:
    def __init__(self, id, in_node, out_node):
        self.id = id
        self.in_node = in_node
        self.out_node = out_node

class Clarify:
    def __init__(self, all_trips):
        self.all_trips = all_trips
        self.trip_edges = self._find_all_trip_edges()
        self.trip_edge_index = None
    
    def _find_all_trip_edges(self):
        sys.stdout.write("\nFinding all trip edges for clarification algorithm... ")
        sys.stdout.flush()
        
        # storage for trip edges
        trip_edges = {} # indexed by trip edge id
        
        # storage for trip edge id
        trip_edge_id = 0
        
        # iterate through all trips
        for trip in self.all_trips:
            
            # iterate through all trip locations
            for i in range(1, len(trip.locations)):
                
                # store current edge
                trip_edges[trip_edge_id] = Edge(trip_edge_id, trip.locations[i-1], trip.locations[i])
                
                # increment trip edge id
                trip_edge_id += 1
        
        print "done."
        
        # return all trip edges
        return trip_edges
    
    def clarify_trips(self):
        print "\nRunning clarification algorithm..."
        
        # storage for clarification round number
        clarification_round = 0
        
        # try until Ctrl-C is pressed, or clarification crashes
        try:
            
            # iterate forever
            while True:
                
                # run clarification algorithm
                curr_clarify_delta = self._run_clarification_algorithm(clarification_round)
                
                # output clarification delta
                print "Clarification delta: " + str(curr_clarify_delta) + " meters"
                
                # write clarified locations to file
                self._write_all_clarified_trips_to_file("round" + str(clarification_round) + "/", curr_clarify_delta)
                
                # increment clarification round
                clarification_round += 1
        
        except KeyboardInterrupt:
            print "aborted.\n"
    
    def _write_all_clarified_trips_to_file(self, subdir, curr_clarify_delta):
        sys.stdout.write("\nWriting all clarified trips to file... ")
        sys.stdout.flush()
        
        # if subdirectory is defined
        if (subdir != ""):
            try:
                # create subdirectory
                os.makedirs("clarified_trips/n" + str(trip_max) + "/" + subdir)
            except:
                pass
        
        # open timestamp file for writing
        timestamp_file = open("clarified_trips/n" + str(trip_max) + "/timestamps.txt", 'a')
        
        # write current time to file
        timestamp_file.write(str(time.time()) + "," + str(subdir[:-1]) + "," + str(curr_clarify_delta) + "\n")
        
        # close timestamp file
        timestamp_file.close()
        
        # open locations file for writing
        locations_file = open("locations_CL.txt", 'w')
        
        # iterate through all trips
        for i in range(0, len(self.all_trips)):
            
            # open trip file
            trip_file = open("clarified_trips/n" + str(trip_max) + "/" + subdir + "trip_" + str(i) + ".txt", 'w')
            
            # write trip location to file
            for trip_location in self.all_trips[i].locations:
                trip_file.write(str(trip_location) + "\n")
                locations_file.write(str(trip_location.latitude) + "," + str(trip_location.longitude) + "\n")
            
            # output newline to denote end of trip
            locations_file.write("\n")
            
            # close trip file
            trip_file.close()
        
        # close locations file
        locations_file.close()
        
        print "done."
    
    def _run_clarification_algorithm(self, clarification_round):
        
        # create update trip edge index
        self.trip_edge_index = self._build_trip_edge_index()
        
        # storage for clarification delta value
        clarify_delta = 0.0
        
        # storage for number of locations
        num_locations = 0.0
        
        # iterate through all trips
        for i in range(0, len(self.all_trips)):
            
            # iterate through all locations
            for location in self.all_trips[i].locations:
                sys.stdout.write("\rClarifying locations for trip " + str(i + 1) + "/" + str(len(self.all_trips)) + "... ")
                sys.stdout.flush()
                
                # grab neighbor edge ids in 100m bounding box
                neighbor_edge_ids = self._find_neighbor_edge_ids(location, 100.0)
                
                # clarify location with its neighbors edges
                clarify_delta += self._clarify_location_with_neighbor_edges(location, neighbor_edge_ids)
                
                # increment location counter
                num_locations += 1.0
        
        # done with this round of clarifications
        print "done (round " + str(clarification_round) + ")."
        
        # move all locations to new coordinates
        self._move_all_locations_to_new_coords()
        
        # return clarification delta
        return (clarify_delta / num_locations)
    
    def _build_trip_edge_index(self):
        sys.stdout.write("\nBuilding trip edge index for clarification algorithm... ")
        sys.stdout.flush()
        
        # storage for trip edge index
        trip_edge_index = Rtree()
        
        # iterate through all trip edges
        for trip_edge in self.trip_edges.values():
            
            # determine trip edge minx, miny, maxx, maxy values
            trip_edge_minx = min(trip_edge.in_node.longitude, trip_edge.out_node.longitude)
            trip_edge_miny = min(trip_edge.in_node.latitude, trip_edge.out_node.latitude)
            trip_edge_maxx = max(trip_edge.in_node.longitude, trip_edge.out_node.longitude)
            trip_edge_maxy = max(trip_edge.in_node.latitude, trip_edge.out_node.latitude)
            
            # insert trip edge into spatial index
            trip_edge_index.insert(trip_edge.id, (trip_edge_minx, trip_edge_miny, trip_edge_maxx, trip_edge_maxy))
        
        print "done."
        
        # return the trip edge index
        return trip_edge_index
    
    def _move_all_locations_to_new_coords(self):
        sys.stdout.write("Moving all locations to new coordinates... ")
        sys.stdout.flush()
        
        # iterate through all trips
        for trip in self.all_trips:
            
            # iterate through all locations
            for location in trip.locations:
                
                # move location from old to new coordinates
                location.latitude = location.new_latitude
                location.longitude = location.new_longitude
        
        print "done."
    
    def _clarify_location_with_neighbor_edges(self, location, neighbor_edge_ids):
        
        # storage for location coordinate deltas
        location_lat_delta = 0.0
        location_lon_delta = 0.0
        
        # determine location's distance from original coordinates
        orig_distance = self._distance_coords(location.latitude, location.longitude, location.orig_latitude, location.orig_longitude)
        
        # determine spring force
        spring_force = (force_step * self._spring_force(orig_distance, spring_force_constant))
        
        # if the location has moved from its original location
        if (orig_distance > 0):
            
            # determine original location coordinate deltas
            orig_location_lat_delta = (location.orig_latitude - location.latitude)
            orig_location_lon_delta = (location.orig_longitude - location.longitude)
            
            # apply spring force
            location_lat_delta += spring_force * ((orig_location_lat_delta * spatialfunclib.METERS_PER_DEGREE_LATITUDE) / orig_distance) / spatialfunclib.METERS_PER_DEGREE_LATITUDE
            location_lon_delta += spring_force * ((orig_location_lon_delta * spatialfunclib.METERS_PER_DEGREE_LONGITUDE) / orig_distance) / spatialfunclib.METERS_PER_DEGREE_LONGITUDE
            
            #print "\nspring force: " + str(spring_force)
            #print "lat: " + `((orig_location_lat_delta * spatialfunclib.METERS_PER_DEGREE_LATITUDE) / orig_distance)`
            #print "lon: " + `((orig_location_lon_delta * spatialfunclib.METERS_PER_DEGREE_LONGITUDE) / orig_distance)`
        
        # iterate through neighbors
        for neighbor_edge_id in neighbor_edge_ids:
            
            # retrieve neighbor edge from trip_edges
            neighbor_edge = self.trip_edges[neighbor_edge_id]
            
            # project location onto neighbor edge
            (neighbor_projection, neighbor_projection_fraction, neighbor_projection_distance) = self._projection_onto_line(neighbor_edge.in_node, neighbor_edge.out_node, location)
            
            # if the location projected onto the neighbor edge
            if (neighbor_projection_fraction >= 0.0 and neighbor_projection_fraction <= 1.0):
                
                # determine neighbor coordinate deltas
                neighbor_lat_delta = (neighbor_projection[0] - location.latitude)
                neighbor_lon_delta = (neighbor_projection[1] - location.longitude)
                
                # determine attraction force (first derivative of normal distribution)
                attraction_force = (neighbor_projection_distance / math.pow(attraction_force_sigma, 2.0)) * self._normal_distribution_pdf(neighbor_projection_distance, 0.0, attraction_force_sigma)
                
                # determine resultant force
                resultant_force = (force_step * attraction_force)
                
                # determine the neighbor projection bearing
                neighbor_projection_bearing = self._path_bearing(neighbor_edge.in_node, neighbor_edge.out_node)
                
                # determine bearing difference between segment and location
                bearing_difference = math.cos(math.radians(neighbor_projection_bearing - self._location_bearing(location)))
                
                # adjust resultant force based on bearing difference
                resultant_force *= bearing_difference
                
                # if segment and location are oriented in opposing directions, determine if location is on right hand side of segment
                if (bearing_difference < 0.0):
                    
                    # if location is on right hand side of segment, set resultant force to 0
                    if (neighbor_projection_bearing >= 0 and neighbor_projection_bearing < 90):
                        
                        if (location.latitude <= neighbor_projection[0] and location.longitude >= neighbor_projection[1]):
                            resultant_force = 0.0
                    
                    elif (neighbor_projection_bearing >= 90 and neighbor_projection_bearing < 180):
                        
                        if (location.latitude <= neighbor_projection[0] and location.longitude <= neighbor_projection[1]):
                            resultant_force = 0.0
                    
                    elif (neighbor_projection_bearing >= 180 and neighbor_projection_bearing < 270):
                        
                        if (location.latitude >= neighbor_projection[0] and location.longitude <= neighbor_projection[1]):
                            resultant_force = 0.0
                    
                    elif (neighbor_projection_bearing >= 270 and neighbor_projection_bearing < 360):
                        
                        if (location.latitude >= neighbor_projection[0] and location.longitude >= neighbor_projection[1]):
                            resultant_force = 0.0
                
                # if the neighbor is not located on the edge
                if (neighbor_projection_distance > 0):
                
                    # adjust location coordinate deltas according to neighbor resultant force
                    location_lat_delta += resultant_force * ((neighbor_lat_delta * spatialfunclib.METERS_PER_DEGREE_LATITUDE) / neighbor_projection_distance) / spatialfunclib.METERS_PER_DEGREE_LATITUDE
                    location_lon_delta += resultant_force * ((neighbor_lon_delta * spatialfunclib.METERS_PER_DEGREE_LONGITUDE) / neighbor_projection_distance) / spatialfunclib.METERS_PER_DEGREE_LONGITUDE
                    
                    #print "\nattractive force: " + str(resultant_force)
                    #print "lat: " + `((neighbor_lat_delta * spatialfunclib.METERS_PER_DEGREE_LATITUDE) / neighbor_projection_distance)`
                    #print "lon: " + `((neighbor_lon_delta * spatialfunclib.METERS_PER_DEGREE_LONGITUDE) / neighbor_projection_distance)`
        
        # store new location coordinates
        location.new_latitude = (location.latitude + location_lat_delta)
        location.new_longitude = (location.longitude + location_lon_delta)
        
        # compute total distance moved
        location_lat_delta_distance = (math.fabs(location_lat_delta) * spatialfunclib.METERS_PER_DEGREE_LATITUDE)
        location_lon_delta_distance = (math.fabs(location_lon_delta) * spatialfunclib.METERS_PER_DEGREE_LONGITUDE)
        
        # return clarification delta
        return math.sqrt(math.pow(location_lat_delta_distance, 2.0) + math.pow(location_lon_delta_distance, 2.0))
    
    def _find_neighbor_edge_ids(self, location, distance):
        
        # define longitude/latitude offset
        lon_offset = ((distance / 2.0) / spatialfunclib.METERS_PER_DEGREE_LONGITUDE)
        lat_offset = ((distance / 2.0) / spatialfunclib.METERS_PER_DEGREE_LATITUDE)
        
        # create bounding box
        bounding_box = (location.longitude - lon_offset, location.latitude - lat_offset, location.longitude + lon_offset, location.latitude + lat_offset)
        
        # return neighbors edge id's inside bounding box
        return list(self.trip_edge_index.intersection(bounding_box))
    
    def _location_bearing(self, location):
        
        # if location has a previous neighbor and a next neighbor
        if ((location.prev_location is not None) and (location.next_location is not None)):
            
            # determine bearing using previous and next neighbors
            return self._path_bearing(location.prev_location, location.next_location)
        
        # if location has no previous neighbor, but has a next neighbor
        elif ((location.prev_location is None) and (location.next_location is not None)):
            
            # determine bearing using current location and next neighbor
            return self._path_bearing(location, location.next_location)
        
        # if location has a previous neighbor, but not a next neighbor
        elif ((location.prev_location is not None) and (location.next_location is None)):
            
            # determine bearing using previous neighbor and current location
            return self._path_bearing(location.prev_location, location)
        
        # if we reach here, there is an error
        return None
    
    def _spring_force(self, x, k):
        return mathfunclib.spring_force(x, k)
    
    def _normal_distribution_pdf(self, x, mu, sigma):
        return mathfunclib.normal_distribution_pdf(x, mu, sigma)
    
    def _projection_onto_line(self, location1, location2, location3):
        return spatialfunclib.projection_onto_line(location1.latitude, location1.longitude, location2.latitude, location2.longitude, location3.latitude, location3.longitude)
    
    def _distance_coords(self, location1_latitude, location1_longitude, location2_latitude, location2_longitude):
        return spatialfunclib.distance(location1_latitude, location1_longitude, location2_latitude, location2_longitude)
    
    def _path_bearing(self, location1, location2):
        return spatialfunclib.path_bearing(location1.latitude, location1.longitude, location2.latitude, location2.longitude)
    
    def _path_bearing_coords(self, location1_latitude, location1_longitude, location2_latitude, location2_longitude):
        return spatialfunclib.path_bearing(location1_latitude, location1_longitude, location2_latitude, location2_longitude)

import sys, getopt
if __name__ == '__main__':
    
    (opts, args) = getopt.getopt(sys.argv[1:],"f:s:a:n:h")
    
    for o,a in opts:
        if o == "-f":
            force_step = float(a)
        if o == "-s":
            spring_force_constant = float(a)
        if o == "-a":
            attraction_force_sigma = float(a)
        if o == "-n":
            trip_max = int(a)
        if o == "-h":
            print "Usage: python cao2009_clarify.py [-f <force_step>] [-s <spring_force_constant>] [-a <attraction_force_sigma>] [-n <trip_max>] [-h]\n"
            exit()
    
    c = Clarify(all_trips[:trip_max])
    c.clarify_trips()
    
    print "\nClarification complete.\n"

