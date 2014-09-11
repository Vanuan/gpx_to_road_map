#
# Implementation of a GPS trace clustering algorithm.
# Author: James P. Biagioni (jbiagi1@uic.edu)
# Company: University of Illinois at Chicago
# Created: 6/15/11
#

import time
import math
import sys
import sqlite3
from pylibs import spatialfunclib, mathfunclib
from location import Location, Trip
from rtree import Rtree
from location import TripLoader

all_trips = TripLoader.get_all_trips("trips/")

# global parameters
cluster_seed_interval = 50.0 # meters
cluster_bearing_difference_limit = math.cos(math.radians(45.0)) # degrees
intra_cluster_distance_limit = 20.0 # meters
edge_bounding_box_size = 80.0 # meters
cluster_distance_moved_threshold = 0.01 # meters per seed
trip_max=len(all_trips)

class Edge:
    def __init__(self, id, in_node, out_node):
        self.id = id
        self.in_node = in_node
        self.out_node = out_node
        self.bearing = spatialfunclib.path_bearing(in_node.latitude, in_node.longitude, out_node.latitude, out_node.longitude)
        self.length = spatialfunclib.distance(in_node.latitude, in_node.longitude, out_node.latitude, out_node.longitude)
        self.cluster = None

class TracePoint:
    def __init__(self, latitude, longitude, bearing, parent_edge):
        self.latitude = latitude
        self.longitude = longitude
        self.bearing = bearing
        self.parent_edge = parent_edge
        self.distance = float('infinity')

class ClusterSeed:
    def __init__(self, id, latitude, longitude, bearing):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.bearing = bearing
        self.trace_points = []
    
    def clear_trace_points(self):
        
        # iterate through all trace points
        for trace_point in self.trace_points:
            
            # remove trace point's parent edge cluster association
            trace_point.parent_edge.cluster = None
        
        # remove all trace points
        self.trace_points = []
    
    def add_trace_points(self, trace_points):
        
        # iterate through all trace points
        for trace_point in trace_points:
            
            # determine distance from trace point to cluster
            trace_point.distance = self._distance(trace_point, self)
        
        # sort trace points by distance from cluster
        trace_points.sort(key=lambda x: x.distance)
        
        # iterate through all trace points
        for trace_point in trace_points:
            
            # if trace point's parent edge has not already been clustered and the trace point passes the membership test
            if ((trace_point.parent_edge.cluster is None) and (self._passes_membership_test(trace_point))):
                
                # add trace point to cluster
                self._add_trace_point(trace_point)
    
    def _add_trace_point(self, trace_point):
        
        # add new trace point to list
        self.trace_points.append(trace_point)
        
        # label trace point's parent edge with cluster
        trace_point.parent_edge.cluster = self
    
    def _passes_membership_test(self, trace_point):
        
        # determine bearing difference between cluster seed and trace point
        bearing_difference = math.cos(math.radians(self.bearing - trace_point.bearing))
        
        # if the bearing difference is less than or equal to 45 degrees
        if (bearing_difference >= cluster_bearing_difference_limit):
            
            # if there are no existing member trace points
            if (len(self.trace_points) == 0):
                
                # if trace point is less than 20 meters from cluster location
                if (trace_point.distance <= intra_cluster_distance_limit):
                    
                    # trace point passes membership test
                    return True
            
            # else, if there are existing member trace points
            else:
                
                # find minimum distance to member traces
                minimum_distance = self._minimum_distance_to_member_traces(trace_point)
                
                # if minimum distance is less than 20 meters
                if (minimum_distance <= intra_cluster_distance_limit):
                    
                    # trace point passes membership test
                    return True
        
        # else, trace point fails membership test
        return False
    
    def _minimum_distance_to_member_traces(self, incoming_trace_point):
        
        # storage for minimum distance
        minimum_distance = float('infinity')
        
        # iterate through existing trace points
        for member_trace_point in self.trace_points:
            
            # calculate distance between member trace point and incoming trace point
            trace_distance = self._distance(member_trace_point, incoming_trace_point)
            
            # if trace distance is less than current minimum distance
            if (trace_distance < minimum_distance):
                
                # store current trace distance as minimum distance
                minimum_distance = trace_distance
        
        # return minimum distance
        return minimum_distance
    
    def recompute_cluster_centroid(self):
        
        # if there are no trace points in this cluster
        if (len(self.trace_points) == 0):
            
            # return without moving the cluster
            return 0.0
        
        # re-compute cluster values
        new_latitude = 0.0
        new_longitude = 0.0
        new_bearing_sin = 0.0
        new_bearing_cos = 0.0
        
        # iterate through trace points
        for trace_point in self.trace_points:
            
            # accumulate values from trace points
            new_latitude += trace_point.latitude
            new_longitude += trace_point.longitude
            new_bearing_sin += math.sin(math.radians(trace_point.bearing))
            new_bearing_cos += math.cos(math.radians(trace_point.bearing))
        
        # average latitude and longitude values
        new_latitude = (new_latitude / len(self.trace_points))
        new_longitude = (new_longitude / len(self.trace_points))
        
        # determine distance moved
        distance_moved = self._distance_coords(self.latitude, self.longitude, new_latitude, new_longitude)
        
        # set new cluster values
        self.latitude = new_latitude
        self.longitude = new_longitude
        self.bearing = math.fmod(math.degrees(math.atan2(new_bearing_sin, new_bearing_cos)) + 360.0, 360.0)
        
        # return distance moved
        return distance_moved
    
    def _distance(self, location1, location2):
        return spatialfunclib.distance(location1.latitude, location1.longitude, location2.latitude, location2.longitude)
    
    def _distance_coords(self, location1_latitude, location1_longitude, location2_latitude, location2_longitude):
        return spatialfunclib.distance(location1_latitude, location1_longitude, location2_latitude, location2_longitude)

class Graph:
    def __init__(self, all_trips):
        # trips
        self.all_trips = all_trips
        
        # cluster seeds
        self.cluster_seeds = {}
        self.cluster_seed_id = 0
        self.cluster_seed_index = Rtree()
        
        # graph edges
        self.graph_edges = {} # indexed by "edge id"
        self.graph_edge_id = 0
        self.graph_edge_lookup = {} # indexed by "location1_id,location2_id"
    
    def cluster_traces(self):
        self._create_all_trip_edges()
        self._generate_cluster_seeds()
        self._cluster_seeds_with_traces()
        self._generate_graph_edges()
        self._output_graph_to_db()
    
    def _generate_graph_edges(self):
        
        sys.stdout.write("Generating graph edges... ")
        sys.stdout.flush()
        
        # iterate through all trips
        for trip in self.all_trips:
            
            # grab trip edges
            trip_edges = trip.edges.values()
            
            # put trip edges in order
            trip_edges.sort(key=lambda x: x.id)
            
            # storage for previous cluster
            prev_cluster = None
            
            # iterate through trip edges
            for trip_edge in trip_edges:
                
                # if the current trip edge is clustered
                if (trip_edge.cluster is not None):
                    
                    # create a graph edge between the previous cluster and the current cluster
                    self._create_graph_edge(prev_cluster, trip_edge.cluster)
                    
                    # update previous cluster with current cluster
                    prev_cluster = trip_edge.cluster
        
        # output graph edges
        self._write_graph_edges_to_file()
        
        print "done."
    
    def _create_graph_edge(self, in_node, out_node):
        
        # if in_node or out_node is None
        if ((in_node is None) or (out_node is None)):
            
            # return without doing anything
            return
        
        # see if we can find an existing graph edge with the same nodes
        existing_graph_edge = self._find_graph_edge(in_node, out_node)
        
        # if there is no existing graph edge with the same nodes
        if (existing_graph_edge is None):
            
            # create new graph edge object
            new_graph_edge = Edge(self.graph_edge_id, in_node, out_node)
            
            # add new graph edge to graph edge dictionary
            self.graph_edges[new_graph_edge.id] = new_graph_edge
            
            # add new graph edge to graph edge lookup dictionary
            self.graph_edge_lookup[str(in_node.id) + "," + str(out_node.id)] = new_graph_edge
            
            # increment graph edge id
            self.graph_edge_id += 1
    
    def _find_graph_edge(self, node1, node2):
        
        # generate edge lookup key
        edge_lookup_key = str(node1.id) + "," + str(node2.id)
        
        # if edge is in lookup table
        if (edge_lookup_key in self.graph_edge_lookup.keys()):
            
            # return the matching edge
            return self.graph_edge_lookup[edge_lookup_key]
        
        # if the edge wasn't in the lookup table
        return None
    
    def _cluster_seeds_with_traces(self):
        
        # storage for total cluster distance moved
        total_cluster_distance_moved = float('infinity')
        
        # iterate until total cluster distance moved below threshold
        while (total_cluster_distance_moved >= cluster_distance_moved_threshold):
            
            # find all points on traces and move clusters
            total_cluster_distance_moved = self._find_points_on_traces()
            
            # write cluster seeds to file
            self._write_cluster_seeds_to_file("edelkamp_cluster_seeds_clustered.txt")
    
    def _find_points_on_traces(self):
        
        # counter for cluster seeds
        seed_counter = 1
        
        # storage for total cluster distance moved
        total_cluster_distance_moved = 0.0
        
        # iterate through all cluster seeds
        for cluster_seed in self.cluster_seeds.values():
            
            # clear current trace points from cluster
            cluster_seed.clear_trace_points()
            
            sys.stdout.write("\rFinding intersecting points with cluster " + str(seed_counter) + "/" + str(len(self.cluster_seeds)) + "... ")
            sys.stdout.flush()
            
            # increment seed counter
            seed_counter += 1
            
            # determine leftward cluster bearing
            leftward_bearing = math.fmod((cluster_seed.bearing - 90.0) + 360.0, 360.0)
            
            # determine rightward cluster bearing
            rightward_bearing = math.fmod((cluster_seed.bearing + 90.0) + 360.0, 360.0)
            
            # storage for candidate trace points
            candidate_trace_points = []
            
            # iterate through all trips
            for trip in self.all_trips:
                
                # find leftward intersection points with trip
                candidate_trace_points.extend(self._find_intersection_points(trip, cluster_seed, leftward_bearing))
                
                # find rightward intersection points with trip
                candidate_trace_points.extend(self._find_intersection_points(trip, cluster_seed, rightward_bearing))
            
            # add candidate trace points to cluster
            cluster_seed.add_trace_points(candidate_trace_points)
            
            # recompute cluster centroid
            total_cluster_distance_moved += cluster_seed.recompute_cluster_centroid()
            
            # clear current trace points from cluster
            cluster_seed.clear_trace_points()
            
            # add candidate trace points to cluster, again
            cluster_seed.add_trace_points(candidate_trace_points)
        
        # normalize total cluster distance moved by number of seeds
        total_cluster_distance_moved = (total_cluster_distance_moved / len(self.cluster_seeds.values()))
        
        # and we're done!
        print "done (clusters moved an average of " + str(total_cluster_distance_moved) + " meters)."
        
        # return total cluster distance moved
        return total_cluster_distance_moved
    
    def _find_intersection_points(self, trip, cluster, cluster_bearing):
        
        # find all nearby trip edge id's
        nearby_trip_edge_ids = self._find_nearby_trip_edge_ids(cluster, edge_bounding_box_size, trip.edge_index)
        
        # storage for intersection points
        intersection_points = []
        
        # iterate through all nearby edge id's
        for edge_id in nearby_trip_edge_ids:
            
            # grab current edge
            edge = trip.edges[edge_id]
            
            # determine intersection point between edge and cluster
            intersection_point = self._intersection_point(edge.in_node, edge.bearing, cluster, cluster_bearing)
            
            # if there is an intersection point
            if (intersection_point is not None):
                
                # determine distance from edge in_node to intersection point
                intersection_distance = self._distance_coords(edge.in_node.latitude, edge.in_node.longitude, intersection_point[0], intersection_point[1])
                
                # if intersection distance is less than edge length
                if (intersection_distance <= edge.length):
                    
                    # this edge has a valid intersection point
                    intersection_points.append(TracePoint(intersection_point[0], intersection_point[1], edge.bearing, edge))
        
        # return all intersection points for this trip
        return intersection_points
    
    def _generate_cluster_seeds(self):
        
        # iterate through all trips
        for i in range(0, len(self.all_trips)):
            
            sys.stdout.write("\rCluster seeding trip " + str(i + 1) + "/" + str(len(self.all_trips)) + "... ")
            sys.stdout.flush()
            
            # grab current trip
            trip = self.all_trips[i]
            
            # set last cluster seed distance to zero for first trip location
            trip.locations[0].last_cluster_seed_distance = 0.0
            
            # iterate through all trip locations
            for j in range(1, len(trip.locations)):
                
                # drop cluster seeds along current edge every 50 meters
                self._drop_cluster_seeds_along_edge(trip.locations[j-1], trip.locations[j])
        
        print "done (generated " + str(len(self.cluster_seeds)) + " cluster seeds)."
        
        # write cluster seeds to file
        self._write_cluster_seeds_to_file("edelkamp_cluster_seeds_initial.txt")
    
    def _drop_cluster_seeds_along_edge(self, in_node, out_node):
        
        # determine edge length
        edge_length = self._distance(in_node, out_node)
        
        # determine distance along edge for first cluster seed
        first_cluster_seed_distance = (cluster_seed_interval - in_node.last_cluster_seed_distance)
        
        # storage for relative cluster seed intervals
        rel_cluster_seed_intervals = []
        
        # storage for current cluster seed distance along this edge
        curr_cluster_seed_distance = first_cluster_seed_distance
        
        # determine the relative cluster seed intervals needed for this edge
        while (curr_cluster_seed_distance <= edge_length):
            
            # append current cluster seed distance to relative cluster seed interval list
            rel_cluster_seed_intervals.append(curr_cluster_seed_distance)
            
            # increment current cluster seed distance
            curr_cluster_seed_distance += cluster_seed_interval
        
        # determine bearing of current edge
        edge_bearing = self._path_bearing(in_node, out_node)
        
        # create cluster seeds for edge
        for i in range(0, len(rel_cluster_seed_intervals)):
            
            # determine fraction along current edge to drop cluster seed
            fraction_along = (rel_cluster_seed_intervals[i] / edge_length)
            
            # determine point along line to drop cluster seed
            (new_cluster_seed_latitude, new_cluster_seed_longitude) = self._point_along_line(in_node, out_node, fraction_along)
            
            # locate nearest existing cluster seeds
            closest_cluster_seeds = list(self.cluster_seed_index.nearest((new_cluster_seed_longitude, new_cluster_seed_latitude), 25))
            
            # if there does not exist a closest existing cluster seed
            if (len(closest_cluster_seeds) == 0):
                
                # create a new cluster seed
                new_cluster_seed = self._create_new_cluster_seed(new_cluster_seed_latitude, new_cluster_seed_longitude, edge_bearing)
            
            # else, if there exists a closest existing cluster seed
            elif (len(closest_cluster_seeds) > 0):
                
                # storage for matched cluster seed
                matched_cluster_seed = None
                
                # iterate through closest existing cluster seeds
                for curr_cluster_seed_id in closest_cluster_seeds:
                    
                    # grab current cluster seed
                    curr_cluster_seed = self.cluster_seeds[curr_cluster_seed_id]
                    
                    # compute distance to current cluster seed
                    distance = self._distance_coords(new_cluster_seed_latitude, new_cluster_seed_longitude, curr_cluster_seed.latitude, curr_cluster_seed.longitude)
                    
                    # determine bearing difference between edge and current cluster seed
                    bearing_difference = math.cos(math.radians(edge_bearing - curr_cluster_seed.bearing))
                    
                    # if current cluster is less than 50 meters away and bearing difference is less than or equal to 45 degrees
                    if ((distance <= cluster_seed_interval) and (bearing_difference >= cluster_bearing_difference_limit)):
                        
                        # store current cluster seed as matched cluster seed
                        matched_cluster_seed = curr_cluster_seed
                        
                        # stop searching
                        break
                
                # if there was not a matched cluster seed
                if (matched_cluster_seed is None):
                    
                    # create a new cluster seed
                    new_cluster_seed = self._create_new_cluster_seed(new_cluster_seed_latitude, new_cluster_seed_longitude, edge_bearing)
            
            # update last cluster seed distance
            out_node.last_cluster_seed_distance = self._distance_coords(new_cluster_seed_latitude, new_cluster_seed_longitude, out_node.latitude, out_node.longitude)
        
        # if no cluster seeds were generated along this edge
        if (len(rel_cluster_seed_intervals) == 0):
            
            # update last cluster seed distance
            out_node.last_cluster_seed_distance = (in_node.last_cluster_seed_distance + edge_length)
    
    def _create_new_cluster_seed(self, latitude, longitude, bearing):
        
        # create a new cluster seed
        new_cluster_seed = ClusterSeed(self.cluster_seed_id, latitude, longitude, bearing)
        
        # add new cluster seed to the cluster seeds dictionary
        self.cluster_seeds[new_cluster_seed.id] = new_cluster_seed
        
        # insert new cluster seed into spatial index
        self.cluster_seed_index.insert(new_cluster_seed.id, (new_cluster_seed.longitude, new_cluster_seed.latitude))
        
        # increment cluster seed id
        self.cluster_seed_id += 1
        
        # return new cluster seed
        return new_cluster_seed
    
    def _create_all_trip_edges(self):
        
        sys.stdout.write("Creating and indexing edges for all trips... ")
        sys.stdout.flush()
        
        # iterate through all trips
        for trip in self.all_trips:
            
            # add edge storage to trip
            trip.edges = {}
            
            # add edge index to trip
            trip.edge_index = Rtree()
            
            # storage for edge id
            trip_edge_id = 0
            
            # iterate through all trip locations
            for i in range(1, len(trip.locations)):
                
                # create new edge
                new_edge = Edge(trip_edge_id, trip.locations[i-1], trip.locations[i])
                
                # insert edge into dictionary
                trip.edges[trip_edge_id] = new_edge
                
                # insert edge into index
                self._index_trip_edge(new_edge, trip.edge_index)
                
                # increment trip edge id
                trip_edge_id += 1
        
        # done
        print "done."
    
    def _index_trip_edge(self, edge, edge_index):
        
        # determine edge minx, miny, maxx, maxy values
        edge_minx = min(edge.in_node.longitude, edge.out_node.longitude)
        edge_miny = min(edge.in_node.latitude, edge.out_node.latitude)
        edge_maxx = max(edge.in_node.longitude, edge.out_node.longitude)
        edge_maxy = max(edge.in_node.latitude, edge.out_node.latitude)
        
        # insert edge into spatial index
        edge_index.insert(edge.id, (edge_minx, edge_miny, edge_maxx, edge_maxy))
    
    def _find_nearby_trip_edge_ids(self, location, distance, edge_index):
        
        # define longitude/latitude offset
        lon_offset = ((distance / 2.0) / spatialfunclib.METERS_PER_DEGREE_LONGITUDE)
        lat_offset = ((distance / 2.0) / spatialfunclib.METERS_PER_DEGREE_LATITUDE)
        
        # create bounding box
        bounding_box = (location.longitude - lon_offset, location.latitude - lat_offset, location.longitude + lon_offset, location.latitude + lat_offset)
        
        # return nearby edge id's inside bounding box
        return list(edge_index.intersection(bounding_box))
    
    def _intersection_point(self, location1, location1_bearing, location2, location2_bearing):
        return spatialfunclib.intersection_point(location1.latitude, location1.longitude, location1_bearing, location2.latitude, location2.longitude, location2_bearing)
    
    def _point_along_line(self, location1, location2, fraction_along):
        return spatialfunclib.point_along_line(location1.latitude, location1.longitude, location2.latitude, location2.longitude, fraction_along)
    
    def _path_bearing(self, location1, location2):
        return spatialfunclib.path_bearing(location1.latitude, location1.longitude, location2.latitude, location2.longitude)
    
    def _distance(self, location1, location2):
        return spatialfunclib.distance(location1.latitude, location1.longitude, location2.latitude, location2.longitude)
    
    def _distance_coords(self, location1_latitude, location1_longitude, location2_latitude, location2_longitude):
        return spatialfunclib.distance(location1_latitude, location1_longitude, location2_latitude, location2_longitude)
    
    def _write_cluster_seeds_to_file(self, filename="edelkamp_cluster_seeds.txt"):
        
        # open graph file
        graph_file = open(filename, 'w')
        
        # iterate through all cluster_seeds
        for cluster_seed in self.cluster_seeds.values():
            
            # output cluster seed to file
            graph_file.write(str(cluster_seed.latitude) + "," + str(cluster_seed.longitude) + "," + str(cluster_seed.bearing) + "\n")
        
        # close graph file
        graph_file.close()
    
    def _write_graph_edges_to_file(self):
        
        # open graph file
        graph_file = open('edelkamp_cluster_edges.txt', 'w')
        
        # iterate through all graph_edges
        for graph_edge in self.graph_edges.values():
            
            # output edge to file
            graph_file.write(str(graph_edge.in_node.latitude) + "," + str(graph_edge.in_node.longitude) + "\n")
            graph_file.write(str(graph_edge.out_node.latitude) + "," + str(graph_edge.out_node.longitude) + "\n\n")
        
        # close graph file
        graph_file.close()
    
    def _output_graph_to_db(self):
        
        # output that we are starting the database writing process...
        sys.stdout.write("\nOutputting graph to database... ")
        sys.stdout.flush()
        
        # connect to database
        conn = sqlite3.connect("edelkamp_graph.db")
        
        # grab cursor
        cur = conn.cursor()
        
        # create nodes table
        cur.execute("CREATE TABLE nodes (id INTEGER, latitude FLOAT, longitude FLOAT)")
        
        # create edges table
        cur.execute("CREATE TABLE edges (id INTEGER, in_node INTEGER, out_node INTEGER)")
        
        # remove values from nodes table
        #cur.execute("DELETE FROM nodes")
        
        # remove values from edges table
        #cur.execute("DELETE FROM edges")
        
        # commit creates
        conn.commit()
        
        # iterate through all cluster seeds
        for cluster_seed in self.cluster_seeds.values():
            
            # insert cluster seed into nodes table
            cur.execute("INSERT INTO nodes VALUES (" + str(cluster_seed.id) + "," + str(cluster_seed.latitude) + "," + str(cluster_seed.longitude) + ")")
        
        # iterate through all graph edges
        for graph_edge in self.graph_edges.values():
            
            # insert graph edge into edges table
            cur.execute("INSERT INTO edges VALUES (" + str(graph_edge.id) + "," + str(graph_edge.in_node.id) + "," + str(graph_edge.out_node.id) + ")")
        
        # commit inserts
        conn.commit()
        
        # close database connection
        conn.close()
        
        print "done."

import sys, getopt, time
from location import TripLoader
if __name__ == '__main__':
    
    (opts, args) = getopt.getopt(sys.argv[1:],"i:b:d:s:t:n:h")
    
    for o,a in opts:
        if o == "-i":
            cluster_seed_interval = float(a)
        if o == "-b":
            cluster_bearing_difference_limit = math.cos(math.radians(float(a)))
        if o == "-d":
            intra_cluster_distance_limit = float(a)
        if o == "-s":
            edge_bounding_box_size = float(a)
        if o == "-t":
            cluster_distance_moved_threshold = float(a)
        if o == "-n":
            trip_max = int(a)
        if o == "-h":
            print "Usage: python edelkamp2003.py [-i <cluster_seed_interval>] [-b <cluster_bearing_difference_limit>] [-d <intra_cluster_distance_limit>] [-s <edge_bounding_box_size>] [-t <cluster_distance_moved_threshold>] [-n <trip_max>] [-h]\n"
            exit()
    
    start_time = time.time()
    g = Graph(all_trips[:trip_max])
    g.cluster_traces()
    
    print "\nEdelkamp clustering complete (in " + str(time.time() - start_time) + " seconds).\n"
