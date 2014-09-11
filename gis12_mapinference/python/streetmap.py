#
# Class to create and store a street map.
# Author: James P. Biagioni (jbiagi1@uic.edu)
# Company: University of Illinois at Chicago
# Created: 6/6/11
#

import sqlite3
import pyximport; pyximport.install()
from pylibs import spatialfunclib
from pylibs import spatialfunclib_accel
from rtree import Rtree

# global parameters
intersection_size = 50.0 # meters

class Node:
    id_counter = 1

    def __init__(self, latitude, longitude, id=None, weight=0.0):
	if id is not None:
            Node.id_counter = max(Node.id_counter, id+1)
	else:
            id = Node.id_counter
            Node.id_counter += 1
 
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.weight = weight
        self.in_nodes = []
        self.out_nodes = []
        self.intersection = None
        self.visited = False

    def coords(self):
        return (self.latitude,self.longitude)

    def distance_to(self, lat, lon):
#        return spatialfunclib.distance(self.latitude, self.longitude, lat, lon)
        return spatialfunclib_accel.fast_distance(self.latitude, self.longitude, lat, lon)

class Edge:
    id_counter = 1
    def __init__(self, in_node, out_node, id=None, weight=0.0, segment=None):
	if id is not None:
            Edge.id_counter = max(Edge.id_counter, id+1)
	else:
            id = Edge.id_counter
            Edge.id_counter += 1 

	self.id = id
        self.in_node = in_node
        self.out_node = out_node
        self.weight = weight
	self.segment = segment
        self.in_edges = []
        self.out_edges = []
        self.visited = False
    
    @property
    def length(self):
        return spatialfunclib.distance(self.in_node.latitude, self.in_node.longitude, self.out_node.latitude, self.out_node.longitude)
    
    @property
    def bearing(self):
        return spatialfunclib.path_bearing(self.in_node.latitude, self.in_node.longitude, self.out_node.latitude, self.out_node.longitude)
    def point_at_meters_along(self, meters):	
	return spatialfunclib.point_along_line(self.in_node.latitude, self.in_node.longitude, self.out_node.latitude, self.out_node.longitude, meters/self.length)	

class Segment:
    id_counter = 1
    def __init__(self, id=None, edges=[]):
	if id is not None:
            Segment.id_counter = max(Segment.id_counter, id+1)
	else:
            id = Segment.id_counter
            Segment.id_counter += 1

        self.id = id
        self.edges = edges
    
    @property
    def head_edge(self):
        return self.edges[0]

    @property
    def length(self):
	sum = 0.0
	for edge in self.edges:
	    sum+=edge.length
	return sum	

    @property
    def tail_edge(self):
        return self.edges[-1]

    # if you get Nones in this list, that's because you didn't set the segment in the Edge
    def out_segments(self):
	return [x.segment for x in self.edges[-1].out_edges]

    # if you get Nones in this list, that's because you didn't set the segment in the Edge
    def in_segments(self):
	return [x.segment for x in self.edges[0].in_edges]

class Intersection:
    def __init__(self, id, nodes):
        self.id = id
        self.nodes = nodes
        (self.latitude, self.longitude) = self._find_mean_location(nodes)
    
    def _find_mean_location(self, nodes):
        
        # initialize location
        latitude = 0.0
        longitude = 0.0
        
        # iterate through member nodes
        for node in self.nodes:
            
            # accumulate values from nodes
            latitude += node.latitude
            longitude += node.longitude
            
            # set node's intersection attribute value
            node.intersection = self
        
        # average latitude and longitude values
        latitude = (latitude / len(self.nodes))
        longitude = (longitude / len(self.nodes))
        
        # return location
        return (latitude, longitude)

class StreetMap:
    def __init__(self):
        self.nodes = {} # indexed by node id
        self.edges = {} # indexed by edge id
        self.intersections = {} # indexed by node id
        self.node_spatial_index = Rtree()
        self.edge_spatial_index = Rtree()
        self.intersection_spatial_index = Rtree()
        self.edge_lookup_table = {} # indexed by (in_node,out_node)
        self.edge_coords_lookup_table = {} # indexed by (in_node.coords, out_node.coords)
        self.segments = {} # indexed by segment id
        self.segment_lookup_table = {} # indexed by (head_edge.in_node, tail_edge.out_node)
    
    def load_osmdb(self, osmdb_filename):
        
        # connect to OSMDB
        conn = sqlite3.connect(osmdb_filename)
        
        # grab cursor
        cur = conn.cursor()
        
        # output that we are loading nodes
        sys.stdout.write("\nLoading nodes... ")
        sys.stdout.flush()
        
        # execute query on nodes table
        cur.execute("select id, lat, lon from nodes")
        query_result = cur.fetchall()
        
        # iterate through all query results
        for id, lat, lon in query_result:
            
            # create and store node in nodes dictionary
            self.nodes[int(id)] = Node(float(lat), float(lon), int(id))
        
        print "done."
        
        # output that we are loading edges
        sys.stdout.write("Loading edges... ")
        sys.stdout.flush()
        
        # execute query on ways table
        cur.execute("select id, tags, nds from ways")
        query_result = cur.fetchall()
        
        # storage for nodes used in valid edges
        valid_edge_nodes = {} # indexed by node id
        
        # iterate through all query results
        for id, tags, nodes in query_result:
            
            # grab tags associated with current way
            way_tags_dict = eval(tags)
            
            # if current way is a valid highway
            if ('highway' in way_tags_dict.keys() and self._valid_highway_edge(way_tags_dict['highway'])):
                
                # grab all nodes that compose this way
                way_nodes_list = eval(nodes)
                
                # iterate through list of way nodes
                for i in range(1, len(way_nodes_list)):
                    
                    # grab in_node from nodes dictionary
                    in_node = self.nodes[int(way_nodes_list[i - 1])]
                    
                    # grab out_node from nodes dictionary
                    out_node = self.nodes[int(way_nodes_list[i])]
                    
                    # create edge_id based on way id
                    edge_id = int(str(id) + str(i - 1) + "000000")
                    
                    # if either node on the edge is valid
                    if (True): #self._valid_node(in_node) or self._valid_node(out_node)):
                        
                        # create and store edge in edges dictionary
                        self.edges[int(edge_id)] = Edge(in_node, out_node,int(edge_id))
                        
                        # store in_node in out_node's in_nodes list
                        if (in_node not in out_node.in_nodes):
                            out_node.in_nodes.append(in_node)
                        
                        # store out_node in in_node's out_nodes list
                        if (out_node not in in_node.out_nodes):
                            in_node.out_nodes.append(out_node)
                        
                        # if edge is bidirectional
                        if ('oneway' not in way_tags_dict.keys()):
                            
                            # create new symmetric edge id
                            symmetric_edge_id = int(str(edge_id / 10) + "1")
                            
                            # create and store symmetric edge in edges dictionary
                            self.edges[int(symmetric_edge_id)] = Edge(out_node, in_node, int(symmetric_edge_id))
                            
                            # store in_node in out_node's out_nodes list
                            if (in_node not in out_node.out_nodes):
                                out_node.out_nodes.append(in_node)
                            
                            # store out_node in in_node's in_nodes list
                            if (out_node not in in_node.in_nodes):
                                in_node.in_nodes.append(out_node)
                        
                        # store in_node in valid_edge_nodes dictionary
                        if (in_node.id not in valid_edge_nodes.keys()):
                            valid_edge_nodes[in_node.id] = in_node
                        
                        # store out_node in valid_edge_nodes dictionary
                        if (out_node.id not in valid_edge_nodes.keys()):
                            valid_edge_nodes[out_node.id] = out_node
        
        print "done."
        
        # close connection to OSMDB
        conn.close()
        
        # replace all nodes with valid edge nodes
        self.nodes = valid_edge_nodes
        
        # index nodes
        self._index_nodes()
        
        # index edges
        self._index_edges()
        
        # find and index intersections
        self._find_and_index_intersections()
        
        # output map statistics
        print "Map has " + str(len(self.nodes)) + " nodes, " + str(len(self.edges)) + " edges and " + str(len(self.intersections)) + " intersections."
    
    def load_graphdb(self, grapdb_filename):
        
        # connect to graph database
        conn = sqlite3.connect(grapdb_filename)
        
        # grab cursor
        cur = conn.cursor()
        
        # output that we are loading nodes
        sys.stdout.write("\nLoading nodes... ")
        sys.stdout.flush()
        
        # execute query on nodes table
        cur.execute("select id, latitude, longitude, weight from nodes")
        query_result = cur.fetchall()
        
        # iterate through all query results
        for id, latitude, longitude, weight in query_result:
            
            # create and store node in nodes dictionary
            self.nodes[id] = Node(latitude, longitude, id, weight)
        
        print "done."
        
        # output that we are loading edges
        sys.stdout.write("Loading edges... ")
        sys.stdout.flush()
        
        # execute query on ways table
        cur.execute("select id, in_node, out_node, weight from edges")
        query_result = cur.fetchall()
        
        # storage for nodes used in valid edges
        valid_edge_nodes = {} # indexed by node id
        
        # iterate through all query results
        for id, in_node_id, out_node_id, weight in query_result:
            
            # grab in_node from nodes dictionary
            in_node = self.nodes[in_node_id]
            
            # grab out_node from nodes dictionary
            out_node = self.nodes[out_node_id]
            
            # if either node on the edge is valid
            if (True): #self._valid_node(in_node) or self._valid_node(out_node)):
                
                # create and store edge in edges dictionary
                self.edges[id] = Edge(in_node, out_node, id, weight)
                
                # store in_node in out_node's in_nodes list
                if (in_node not in out_node.in_nodes):
                    out_node.in_nodes.append(in_node)
                
                # store out_node in in_node's out_nodes list
                if (out_node not in in_node.out_nodes):
                    in_node.out_nodes.append(out_node)
                
                # store in_node in valid_edge_nodes dictionary
                if (in_node.id not in valid_edge_nodes.keys()):
                    valid_edge_nodes[in_node.id] = in_node
                
                # store out_node in valid_edge_nodes dictionary
                if (out_node.id not in valid_edge_nodes.keys()):
                    valid_edge_nodes[out_node.id] = out_node
        
        # execute query on segments table
        cur.execute("select id, edge_ids from segments")
        query_result = cur.fetchall()
        
        for id, edge_ids in query_result:
            segment_edges = map(lambda edge_id: self.edges[edge_id], eval(edge_ids))
            self.segments[id] = Segment(id, segment_edges)
            
            self.segment_lookup_table[(self.segments[id].head_edge.in_node, self.segments[id].tail_edge.out_node)] = self.segments[id]
            
            for segment_edge in segment_edges:
		segment_edge.segment = self.segments[id] 
#                self.segment_lookup_table[segment_edge.id] = self.segments[id]
        
        # execute query on intersections table
        cur.execute("select node_id from intersections")
        query_result = cur.fetchall()
        
        for node_id in query_result:
            self.intersections[node_id[0]] = self.nodes[node_id[0]]
        

        try:
            cur.execute("select transition_segment, from_segment, to_segment from transitions");
            query_result = cur.fetchall()
            self.transitions={}
            for transition_segment, from_segment, to_segment in query_result:
                self.transitions[transition_segment]=(from_segment,to_segment)
        except:
            print "Got an error reading "
            
        print "done."
        
        # close connection to graph db
        conn.close()
        
        # replace all nodes with valid edge nodes
        self.nodes = valid_edge_nodes
        
        # index nodes
        self._index_nodes()
        
        # index edges
        self._index_edges()
        
        # find and index intersections
        #self._find_and_index_intersections()
        
        # output map statistics
        print "Map has " + str(len(self.nodes)) + " nodes, " + str(len(self.edges)) + " edges, " + str(len(self.segments)) + " segments and " + str(len(self.intersections)) + " intersections."
    
    def load_shapedb(self, shapedb_filename):
        
        # connect to graph database
        conn = sqlite3.connect(shapedb_filename)
        
        # grab cursor
        cur = conn.cursor()
        
        # execute query to find all shape ids
        cur.execute("select distinct shape_id from shapes")
        
        # output that we are loading nodes and edges
        sys.stdout.write("\nLoading nodes and edges... ")
        sys.stdout.flush()
        
        # storage for shape specific edges
        self.shape_edges = {} # indexed by shape_id
        
        # storage for node id
        node_id = 0
        
        # iterate through all shape ids
        for shape_id in cur.fetchall():
            
            # grab shape id
            shape_id = shape_id[0]
            
            # if route is a bus route
            if (shape_id == "0" or shape_id == "11" or shape_id == "15" or shape_id == "41" or shape_id == "65" or shape_id == "22"):
                
                # execute query to find all shape points
                cur.execute("select shape_pt_lat, shape_pt_lon from shapes where shape_id='" + str(shape_id) + "' order by shape_pt_sequence asc")
                
                # amend shape id
                if (shape_id == "0"):
                    shape_id = "10000000"
                elif (shape_id == "11"):
                    shape_id = "10000011"
                elif (shape_id == "41"):
                    shape_id = "10000041"
                elif (shape_id == "15"):
                    shape_id = "10000015"
                elif (shape_id == "65"):
                    shape_id = "10000065"
                elif (shape_id == "22"):
                    shape_id = "10000022"
                
                # storage for first node
                first_node = None
                
                # storage for previous node
                prev_node = None
                
                # create list for this shape's edges
                self.shape_edges[shape_id] = []
                
                # iterate through all shape points
                for shape_pt_lat, shape_pt_lon in cur.fetchall():
                    
                    # create new node
                    curr_node = Node(shape_pt_lat, shape_pt_lon, node_id)
                    
                    # store first node
                    if (first_node is None):
                        first_node = curr_node
                    
                    # increment node id
                    node_id += 1
                    
                    # add shape id to node
                    curr_node.shape_id = shape_id
                    
                    # store new node in nodes dictionary
                    self.nodes[node_id] = curr_node
                    
                    # if there exists a previous node
                    if (prev_node is not None):
                        
                        # create edge id
                        edge_id = int(str(shape_id) + str(prev_node.id) + str(curr_node.id))
                        
                        # create new edge
                        curr_edge = Edge(prev_node, curr_node, edge_id)
                        
                        # add shape id to edge
                        curr_edge.shape_id = shape_id
                        
                        # store new edge in edges dictionary
                        self.edges[edge_id] = curr_edge
                        
                        # store new edge in shape edges dictionary
                        self.shape_edges[shape_id].append(curr_edge)
                        
                        # store previous node in current node's in_nodes list
                        curr_node.in_nodes.append(prev_node)
                        
                        # store current node in previous node's out_nodes list
                        prev_node.out_nodes.append(curr_node)
                    
                    # update previous node
                    prev_node = curr_node
                
                # create edge id for last edge
                edge_id = int(str(shape_id) + str(prev_node.id) + str(first_node.id))
                
                # create new edge
                curr_edge = Edge(prev_node, first_node, edge_id)
                
                # add shape id to edge
                curr_edge.shape_id = shape_id
                
                # store new edge in edges dictionary
                self.edges[edge_id] = curr_edge
                
                # store new edge in shape edges dictionary
                self.shape_edges[shape_id].append(curr_edge)
                
                # store previous node in first node's in_nodes list
                first_node.in_nodes.append(prev_node)
                
                # store first node in previous node's out_nodes list
                prev_node.out_nodes.append(first_node)
        
        print "done."
        
        # close connection to gtfs db
        conn.close()
        
        # index nodes
        self._index_nodes()
        
        # index edges
        self._index_edges()
        
        # find and index intersections
        self._find_and_index_intersections()
        
        # output map statistics
        print "Map has " + str(len(self.nodes)) + " nodes, " + str(len(self.edges)) + " edges and " + str(len(self.intersections)) + " intersections."
    
    def _index_nodes(self):
        
        # output that we are indexing nodes
        sys.stdout.write("Indexing nodes... ")
        sys.stdout.flush()
        
        # iterate through all nodes
        for curr_node in self.nodes.values():
            
            # insert node into spatial index
            self.node_spatial_index.insert(curr_node.id, (curr_node.longitude, curr_node.latitude))
        
        print "done."
    
    def _index_edges(self):
        
        # output that we are indexing edges
        sys.stdout.write("Indexing edges... ")
        sys.stdout.flush()
        
        # iterate through all edges
        for curr_edge in self.edges.values():
            
            # determine current edge minx, miny, maxx, maxy values
            curr_edge_minx = min(curr_edge.in_node.longitude, curr_edge.out_node.longitude)
            curr_edge_miny = min(curr_edge.in_node.latitude, curr_edge.out_node.latitude)
            curr_edge_maxx = max(curr_edge.in_node.longitude, curr_edge.out_node.longitude)
            curr_edge_maxy = max(curr_edge.in_node.latitude, curr_edge.out_node.latitude)
            
            # insert current edge into spatial index
            self.edge_spatial_index.insert(curr_edge.id, (curr_edge_minx, curr_edge_miny, curr_edge_maxx, curr_edge_maxy))
            
            # insert current edge into lookup table
            self.edge_lookup_table[(curr_edge.in_node, curr_edge.out_node)] = curr_edge
            self.edge_coords_lookup_table[(curr_edge.in_node.coords(), curr_edge.out_node.coords())] = curr_edge
        
        # iterate through all edges
        for edge in self.edges.values():
            
            # iterate through all out edges
            for out_node_neighbor in edge.out_node.out_nodes:
                
                # add out edge to out edges list
                edge.out_edges.append(self.edge_lookup_table[(edge.out_node, out_node_neighbor)])
            
            # iterate through all in edges
            for in_node_neighbor in edge.in_node.in_nodes:
                
                # add in edge to in edges list
                edge.in_edges.append(self.edge_lookup_table[(in_node_neighbor, edge.in_node)])
        
        print "done."
    
    def _find_and_index_intersections(self):
        
        # output that we are finding and indexing intersections
        sys.stdout.write("Finding and indexing intersections... ")
        sys.stdout.flush()
        
        # find intersection nodes and index
        (intersection_nodes, intersection_nodes_index) = self._find_intersection_nodes()
        
        # storage for intersection nodes already placed in intersections
        placed_intersection_nodes = set()
        
        # define longitude/latitude offset for bounding box
        lon_offset = ((intersection_size / 2.0) / spatialfunclib.METERS_PER_DEGREE_LONGITUDE)
        lat_offset = ((intersection_size / 2.0) / spatialfunclib.METERS_PER_DEGREE_LATITUDE)
        
        # storage for intersection id
        intersection_id = 0
        
        # iterate through intersection nodes
        for intersection_node in intersection_nodes:
            
            # if the intersection node has not yet been placed
            if (intersection_node not in placed_intersection_nodes):
                
                # create bounding box
                bounding_box = (intersection_node.longitude - lon_offset, intersection_node.latitude - lat_offset, intersection_node.longitude + lon_offset, intersection_node.latitude + lat_offset)
                
                # find intersection node ids within bounding box
                intersection_node_ids = intersection_nodes_index.intersection(bounding_box)
                
                # get intersection nodes
                intersection_nodes = map(self._get_node, intersection_node_ids)
                
                # add intersection nodes to placed set
                placed_intersection_nodes.update(intersection_nodes)
                
                # create new intersection
                new_intersection = Intersection(intersection_id, intersection_nodes)
                
                # increment intersection id
                intersection_id += 1
                
                # add new intersection to intersections list
                self.intersections[new_intersection.id] = new_intersection
                
                # insert new intersection into spatial index
                self.intersection_spatial_index.insert(new_intersection.id, (new_intersection.longitude, new_intersection.latitude))
        
        print "done."
    
    def _get_node(self, node_id):
        
        # return node from dictionary
        return self.nodes[node_id]
    
    def _find_intersection_nodes(self):
        
        # storage for intersection nodes
        intersection_nodes = []
        
        # spatial index for intersection nodes
        intersection_nodes_index = Rtree()
        
        # iterate through all nodes in map
        for curr_node in self.nodes.values():
            
            # set storage for current node's unique neighbors
            neighbors = set()
            
            # iterate through all in_nodes
            for in_node in curr_node.in_nodes:
                
                # add in_node to neighbors set
                neighbors.add(in_node)
            
            # iterate through all out_nodes
            for out_node in curr_node.out_nodes:
                
                # add out_node to neighbors set
                neighbors.add(out_node)
            
            # if current node has more than 2 neighbors
            if (len(neighbors) > 2):
                
                # add current node to intersection nodes list
                intersection_nodes.append(curr_node)
                
                # add current node to intersection nodes index
                intersection_nodes_index.insert(curr_node.id, (curr_node.longitude, curr_node.latitude))
        
        # return intersection nodes and index
        return (intersection_nodes, intersection_nodes_index)
    
    def _valid_node(self, node):
        
        # if node falls inside the designated bounding box
        if ((node.latitude >= 41.8619 and node.latitude <= 41.8842) and
            (node.longitude >= -87.6874 and node.longitude <= -87.6398)):
            
            return True
        else:
            return False
    
    def _valid_highway_edge(self, highway_tag_value):
        if ((highway_tag_value == 'primary') or 
            (highway_tag_value == 'secondary') or 
            (highway_tag_value == 'tertiary') or 
            (highway_tag_value == 'residential')):
            
            return True
        else:
            return False
    
    def reset_node_visited_flags(self):
        
        # iterate through all nodes
        for node in self.nodes.values():
            
            # set node visited flag to False
            node.visited = False
    
    def reset_edge_visited_flags(self):
        
        # iterate through all edges
        for edge in self.edges.values():
            
            # set edge visited flag to False
            edge.visited = False
    
    def write_map_to_file(self, map_filename="map.txt"):
        
        # output that we are starting the writing process
        sys.stdout.write("\nWriting map to file... ")
        sys.stdout.flush()
        
        # open map file
        map_file = open(map_filename, 'w')
        
        # iterate through all map edges
        for curr_edge in self.edges.values():
            
            # output current edge to file
            map_file.write(str(curr_edge.in_node.latitude) + "," + str(curr_edge.in_node.longitude) + "\n")
            map_file.write(str(curr_edge.out_node.latitude) + "," + str(curr_edge.out_node.longitude) + "\n\n")
        
        # close map file
        map_file.close()
        
        print "done."
    
    def _distance(self, location1, location2):
        return spatialfunclib.distance(location1.latitude, location1.longitude, location2.latitude, location2.longitude)

import sys
import time
if __name__ == '__main__':
    usage = "usage: python streetmap.py (osmdb|graphdb|shapedb) db_filename output_filename"
    
    if len(sys.argv) != 4:
        print usage
        exit()
    
    start_time = time.time()
    db_type = sys.argv[1]
    db_filename = sys.argv[2]
    output_filename = sys.argv[3]
    
    m = StreetMap()
    
    if (db_type == "osmdb"):
        m.load_osmdb(db_filename)
        m.write_map_to_file(str(output_filename))
    
    elif (db_type == "graphdb"):
        m.load_graphdb(db_filename)
        m.write_map_to_file(str(output_filename))
    
    elif (db_type == "shapedb"):
        m.load_shapedb(db_filename)
        m.write_map_to_file(str(output_filename))
    
    else:
        print "Error! '" + str(db_type) + "' is an unknown database type"
    
    print "\nMap operations complete (in " + str(time.time() - start_time) + " seconds).\n"
