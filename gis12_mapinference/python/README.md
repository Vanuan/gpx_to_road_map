## Article

"Map Inference in the Face of Noise and Disparity" (published in ACM SIGSPATIAL GIS 2012)

# Source
Downloaded from: https://www.cs.uic.edu/bin/view/Bits/Software

Authors: James Biagioni (jbiagi1@uic.edu) and Jakob Eriksson (jakob@uic.edu)
Date: 11/7/2012

## Steps


1. Create KDE (kde.png) from trips

    python kde.py -p trips/trips_1m/

2. Create grayscale skeleton (skeleton.png) from KDE

    python skeleton.py kde.png skeleton.png

3. Extract map database (`skeleton_maps/skeleton_map_1m.db`) from grayscale skeleton

    python graph_extract.py skeleton.png bounding_boxes/bounding_box_1m.txt skeleton_maps/skeleton_map_1m.db

4. Map-match trips onto map database

    python graphdb_matcher_run.py -d skeleton_maps/skeleton_map_1m.db -t trips/trips_1m/ -o trips/matched_trips_1m/

5. Prune map database with map-matched trips, producing pruned map database (`skeleton_maps/skeleton_map_1m_mm1.db`)

    python process_map_matches.py -d skeleton_maps/skeleton_map_1m.db -t trips/matched_trips_1m/ -o skeleton_maps/skeleton_map_1m_mm1.db

6. Refine topology of pruned map, producing refined map (`skeleton_maps/skeleton_map_1m_mm1_tr.db`)

    python refine_topology.py -d skeleton_maps/skeleton_map_1m_mm1.db -t skeleton_maps/skeleton_map_1m_mm1_traces.txt -o skeleton_maps/skeleton_map_1m_mm1_tr.db

7. Map-match trips onto refined map

    python graphdb_matcher_run.py -d skeleton_maps/skeleton_map_1m_mm1_tr.db -t trips/trips_1m/ -o trips/matched_trips_1m_mm1_tr/


8. Prune refined map with map-matched trips, producing pruned refined map database (`skeleton_maps/skeleton_map_1m_mm2.db`)

    python process_map_matches.py -d skeleton_maps/skeleton_map_1m_mm1_tr.db -t trips/matched_trips_1m_mm1_tr/ -o skeleton_maps/skeleton_map_1m_mm2.db


9. Output pruned refined map database for visualization (`final_map.txt`)

    python streetmap.py graphdb skeleton_maps/skeleton_map_1m_mm2.db final_map.txt
