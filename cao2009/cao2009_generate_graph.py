#
# Implementation of a Graph Generation algorithm.
# Author: James P. Biagioni (jbiagi1@uic.edu)
# Company: University of Illinois at Chicago
# Created: 3/1/11
#

import time
import math
import sys
import sqlite3
from pylibs import spatialfunclib, mathfunclib
from rtree import Rtree

# global parameters
max_path_length = 4 # hops
min_graph_edge_volume = 3 # count
location_projection_distance_limit = 20.0 # meters
location_bearing_difference_limit = math.cos(math.radians(45.0)) # degrees

class Edge:
    def __init__(self, id, in_node, out_node):
        self.id = id
        self.in_node = in_node
        self.out_node = out_node
        self.volume = 1

class Graph:
    def __init__(self, bus_trips):
        self.bus_trips = bus_trips
        self.graph_nodes = {} # indexed by "location_id"
        self.graph_edge_id = 0
        self.graph_edges = {} # indexed by "edge id"
        self.graph_edge_lookup = {} # indexed by "location1_id,location2_id"
        self.graph_edge_index = Rtree()
    
    def generate_graph(self):
        print "Running graph generation algorithm..."
        
        # initialize trip counter
        trip_count = 1
        
        for trip in self.bus_trips:
            
            # initialize location counter
            location_count = 1
            
            # storage for previous node
            prev_node = None
            
            for location in trip.locations:
                sys.stdout.write("\rAnalyzing location " + str(location_count) + "/" + str(len(trip.locations)) + " for trip " + str(trip_count) + "/" + str(len(self.bus_trips)) + "... ")
                sys.stdout.flush()
                
                # find closest edges in graph to location
                closest_edges = self._find_closest_edges_in_graph(location, 100)
                
                # flag variable for whether we merged location
                did_merge_location = False
                
                # iterate through candidate edge ids
                for candidate_edge_id in closest_edges:
                    
                    # grab candidate edge from graph edge dictionary
                    candidate_edge = self.graph_edges[candidate_edge_id]
                    
                    # determine whether we should merge with candidate edge
                    if (self._should_merge_location_with_edge(location, candidate_edge) is True):
                        
                        # merge location with edge, update previous node
                        prev_node = self._merge_location_with_edge(location, candidate_edge, prev_node)
                        
                        # update merge flag variable
                        did_merge_location = True
                        
                        # no need to look at further edges, break out of candidate edges loop
                        break
                
                # if we did not merge the location with any edge
                if (did_merge_location is False):
                    
                    # add location to graph
                    self._add_location_to_graph(location, prev_node)
                    
                    # update previous node with current location
                    prev_node = location
                
                # increment location counter
                location_count += 1
            
            # done with current trip locations
            print "done."
            
            # increment trip counter
            trip_count += 1
        
        # write graph edges to file
        self._write_graph_edges_to_file()
        
        # create graph database
        self._output_graph_to_db()
    
    def _merge_location_with_edge(self, location, edge, prev_node):
        
        # get the edge node closest to the location
        edge_node = self._get_closest_edge_node(location, edge)
        
        # if prev_node is None
        if (prev_node is None):
            
            # increase volume of just this edge
            edge.volume += 1
        
        # if prev_node is not None
        else:
            
            # find path from prev_node to edge_node
            path = self._find_path(prev_node, edge_node, max_path_length)
            
            # if there was a path from prev_node to edge_node
            if (path is not None):
                
                # iterate through nodes in path
                for i in range(1, len(path)):
                    
                    # grab in_node
                    in_node = path[i - 1]
                    
                    # grab out_node
                    out_node = path[i]
                    
                    # find corresponding graph edge
                    graph_edge = self._find_graph_edge(in_node, out_node)
                    
                    # increment volume on edge
                    graph_edge.volume += 1
            
            # if there is no path from prev_node to edge_node
            else:
                
                # create a new graph edge between prev_node and edge_node
                self._create_graph_edge(prev_node, edge_node)
        
        # return the edge_node
        return edge_node
    
    def _get_closest_edge_node(self, location, edge):
        
        # if in_node distance is less than out_node distance
        if (self._distance(location, edge.in_node) < self._distance(location, edge.out_node)):
            
            # return the edge in_node
            return edge.in_node
        
        # otherwise, return the edge out_node
        return edge.out_node
    
    def _find_path(self, source, destination, max_length):
        
        # reset all node visited flags
        self._reset_node_visited_flags()
        
        # get a breath-first search path from source to destination
        path = self._bfs_path(source, destination)
        
        # if there is a path from source to destination
        if (path is not None):
            
            # and if the path length is less than or equal to the maximum length
            if (len(path) <= max_length):
                
                # return the path
                return path
        
        # otherwise, return None
        return None
    
    def _bfs_path(self, source, destination):
        
        # storage for breadth-first search parents
        bfs_parent = {} # key is current node, value is parent node
        
        # source node has no breadth-first search parent
        bfs_parent[source] = None
        
        # node queue for breadth-first search
        bfs_queue = []
        
        # enqueue source node
        bfs_queue.append(source)
        
        # mark source node as visited
        source.visited = True
        
        # while the queue is not empty
        while (len(bfs_queue) > 0):
            
            # dequeue the first node in the queue
            curr_node = bfs_queue.pop(0)
            
            # if the current node is the destination
            if (curr_node is destination):
                
                # create storage for breadth-first search path
                bfs_path = []
                
                # add the current node to the breadth-first search path
                bfs_path.insert(0, curr_node)
                
                # grab the parent of the current node
                parent = bfs_parent[curr_node]
                
                # iterate through breadth-first search parents
                while (parent is not None):
                    
                    # add the parent to the breadth-first search path
                    bfs_path.insert(0, parent)
                    
                    # grab the next parent
                    parent = bfs_parent[parent]
                
                # return the breadth-first search path
                return bfs_path
            
            # if the current node is not the destination
            else:
                
                # iterate through the current node's out_nodes
                for out_node in curr_node.out_nodes:
                    
                    # if the out_node has not been visited
                    if (out_node.visited is False):
                        
                        # mark the out_node as visited
                        out_node.visited = True
                        
                        # enqueue the out_node
                        bfs_queue.append(out_node)
                        
                        # store curr_node as out_node's breadth-first search parent
                        bfs_parent[out_node] = curr_node
        
        # if we reached here, no path was found
        return None
    
    def _should_merge_location_with_edge(self, location, edge):
        
        # project location onto edge
        (location_projection, location_projection_fraction, location_projection_distance) = self._projection_onto_line(edge.in_node, edge.out_node, location)
        
        # if projection is not onto edge
        if (location_projection_fraction < 0.0 or location_projection_fraction > 1.0):
            
            # we cannot merge location with edge
            return False
        
        # determine bearing difference between edge and location
        bearing_difference = math.cos(math.radians(self._path_bearing(edge.in_node, edge.out_node) - self._location_bearing(location)))
        
        # if location projection distance is less than 20 meters
        if (location_projection_distance < location_projection_distance_limit):
            
            # if bearing difference is less than 45 degrees
            if (bearing_difference > location_bearing_difference_limit):
                
                # merge location with edge
                return True
        
        # otherwise, do not merge location with edge
        return False
    
    def _add_location_to_graph(self, location, prev_node):
        
        # add an out_nodes list to location
        location.out_nodes = []
        
        # add an in_nodes list to location
        location.in_nodes = []
        
        # add a visited flag to location
        location.visited = False
        
        # add location to graph nodes list
        self.graph_nodes[location.id] = location
        
        # if prev_node is not None
        if (prev_node is not None):
            
            # create a new graph edge between prev_node and location
            self._create_graph_edge(prev_node, location)
    
    def _create_graph_edge(self, in_node, out_node):
        
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
            
            # add new graph edge to graph edges spatial index
            self._add_graph_edge_to_index(new_graph_edge)
            
            # increment graph edge id
            self.graph_edge_id += 1
            
            # store out_node in in_nodes's out_nodes list
            in_node.out_nodes.append(out_node)
            
            # store in_node in out_node's in_nodes list
            out_node.in_nodes.append(in_node)
    
    def _find_graph_edge(self, node1, node2):
        
        # generate edge lookup key
        edge_lookup_key = str(node1.id) + "," + str(node2.id)
        
        # if edge is in lookup table
        if (edge_lookup_key in self.graph_edge_lookup.keys()):
            
            # return the matching edge
            return self.graph_edge_lookup[edge_lookup_key]
        
        # if the edge wasn't in the lookup table
        return None
    
    def _add_graph_edge_to_index(self, graph_edge):
        
        # determine graph edge minx, miny, maxx, maxy values
        graph_edge_minx = min(graph_edge.in_node.longitude, graph_edge.out_node.longitude)
        graph_edge_miny = min(graph_edge.in_node.latitude, graph_edge.out_node.latitude)
        graph_edge_maxx = max(graph_edge.in_node.longitude, graph_edge.out_node.longitude)
        graph_edge_maxy = max(graph_edge.in_node.latitude, graph_edge.out_node.latitude)
        
        # insert graph edge into spatial index
        self.graph_edge_index.insert(graph_edge.id, (graph_edge_minx, graph_edge_miny, graph_edge_maxx, graph_edge_maxy))
    
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
    
    def _find_closest_edges_in_graph(self, location, number_of_edges):
        return self.graph_edge_index.nearest((location.longitude, location.latitude), number_of_edges)
    
    def _projection_onto_line(self, location1, location2, location3):
        return spatialfunclib.projection_onto_line(location1.latitude, location1.longitude, location2.latitude, location2.longitude, location3.latitude, location3.longitude)
    
    def _path_bearing(self, location1, location2):
        return spatialfunclib.path_bearing(location1.latitude, location1.longitude, location2.latitude, location2.longitude)
    
    def _distance(self, location1, location2):
        return spatialfunclib.distance(location1.latitude, location1.longitude, location2.latitude, location2.longitude)
    
    def _output_graph_to_db(self):
        
        # output that we are starting the database writing process...
        sys.stdout.write("\nOutputting graph to database... ")
        sys.stdout.flush()
        
        # connect to database
        conn = sqlite3.connect("cao_graph.db")
        
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
        
        # iterate through all graph nodes
        for graph_node in self.graph_nodes.values():
            
            # insert graph node into nodes table
            cur.execute("INSERT INTO nodes VALUES (" + str(graph_node.id) + "," + str(graph_node.latitude) + "," + str(graph_node.longitude) + ")")
        
        # iterate through all graph edges
        for graph_edge in self.graph_edges.values():
            
            # if the graph edge has volume greater than or equal to 3
            if (graph_edge.volume >= min_graph_edge_volume):
                
                # insert graph edge into edges table
                cur.execute("INSERT INTO edges VALUES (" + str(graph_edge.id) + "," + str(graph_edge.in_node.id) + "," + str(graph_edge.out_node.id) + ")")
        
        # commit inserts
        conn.commit()
        
        # close database connection
        conn.close()
        
        print "done."
    
    def _write_graph_edges_to_file(self):
        
        # output that we are starting the writing process
        sys.stdout.write("\nWriting graph edges to file... ")
        sys.stdout.flush()
        
        # open graph file
        graph_file = open('cao_edges.txt', 'w')
        
        # iterate through all graph_edges
        for graph_edge in self.graph_edges.values():
            
            # if the graph edge has volume greater than or equal to 3
            if (graph_edge.volume >= min_graph_edge_volume):
                
                # output edge to file
                graph_file.write(str(graph_edge.in_node.latitude) + "," + str(graph_edge.in_node.longitude) + "\n")
                graph_file.write(str(graph_edge.out_node.latitude) + "," + str(graph_edge.out_node.longitude) + "," + str(graph_edge.volume) + "\n\n")
        
        # close graph file
        graph_file.close()
        
        print "done."
    
    def _reset_node_visited_flags(self):
        
        # iterate through all graph nodes
        for graph_node in self.graph_nodes.values():
            
            # set visited flag to False
            graph_node.visited = False

import sys, getopt, time
from location import TripLoader
if __name__ == '__main__':
    
    # default values
    trip_round = 0
    trip_max = 889
    
    (opts, args) = getopt.getopt(sys.argv[1:],"p:v:d:b:r:n:h")
    
    for o,a in opts:
        if o == "-p":
            max_path_length = int(a)
        if o == "-v":
            min_graph_edge_volume = int(a)
        if o == "-d":
            location_projection_distance_limit = float(a)
        if o == "-b":
            location_bearing_difference_limit = math.cos(math.radians(float(a)))
        if o == "-r":
            trip_round = int(a)
        if o == "-n":
            trip_max = int(a)
        if o == "-h":
            print "Usage: python cao2009_generate_graph.py [-p <max_path_length>] [-v <min_graph_edge_volume>] [-d <location_projection_distance_limit>] [-b <location_bearing_difference_limit>] [-r <clarified_trips_round>] [-n <trip_max>] [-h]\n"
            exit()
    
    all_trips = TripLoader.get_all_trips("clarified_trips/n" + str(trip_max) + "/round" + str(trip_round) + "/")
    
    start_time = time.time()
    g = Graph(all_trips[:trip_max])
    g.generate_graph()
    
    print "\nGraph generation complete (in " + str(time.time() - start_time) + " seconds).\n"
