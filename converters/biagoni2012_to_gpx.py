import gpxpy
import gpxpy.gpx


gpx = gpxpy.gpx.GPX()

with open('final_map.txt') as f:

  line_points = []
  i = 0
  for line in f.readlines():
    line = line.strip()
    if line:
      y, x = line.split(',')
      line_points.append((y,x))
    else:
      p1 = line_points[0]
      p2 = line_points[1]
#      print "%s, %s, %s" % (i, p1[0], p1[1])
#      print "%s, %s, %s" % (i+1, p2[0], p2[1])
#      i += 2
      line_points = []
      gpx_track = gpxpy.gpx.GPXTrack()
      gpx.tracks.append(gpx_track)
      gpx_segment = gpxpy.gpx.GPXTrackSegment()
      gpx_track.segments.append(gpx_segment)
      gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(p1[1], p1[0]))
      gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(p2[1], p2[0]))
  with open('final_map.gpx', 'w') as fw:    
    fw.write(gpx.to_xml())
