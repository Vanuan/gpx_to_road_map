import sys

def writeOSM(filename, vertices, edges):
  with open(filename, "w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>')
    f.write('<osm version="0.6" generator="gpx_to_map">')
    for id, lat, lon in vertices:
      f.write('<node id="%s" lat="%s" lon="%s"/>' % (-int(id)-1, lat, lon))
    for id, edge in enumerate(edges):
      p1, p2 = edge
      f.write('<way id="%s">' % (-int(id)-1))
      f.write('<nd ref="%s"/>' % (-int(p1)-1))
      f.write('<nd ref="%s"/>' % (-int(p2)-1))
      f.write('</way>')
    f.write('</osm>')

if __name__ == '__main__':
  input_dir = sys.argv[1]
  output_file = sys.argv[2]
  if len(sys.argv) != 3:
    print "Usage: %s <input_dir> <output_file>"
    sys.exit(0)

  edges = []
  vertices = []
  for vertex in open("%s/vertices.txt" % input_dir):
    id, lat, lon = vertex.split(" ")
    vertices.append((id, lat, lon))

  for edge in open("%s/edges.txt" % input_dir):
    p1, p2 = edge.split(" ")
    edges.append((p1, p2))

  writeOSM(output_file, vertices, edges)
  print "%s written" % output_file
