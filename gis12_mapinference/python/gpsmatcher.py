from viterbi import Viterbi
from rtree import Rtree
from spatialfunclib import *

class GPSMatcher:
    def __init__(self, hmm, emission_probability, constraint_length=10, MAX_DIST=500, priors=None, smallV=0.00000000001):                
        # initialize spatial index
        self.previous_obs = None

        if priors == None:
            priors=dict([(state,1.0/len(hmm)) for state in hmm])

        state_spatial_index = Rtree()
        unlocated_states = []
        id_to_state = {}
        id = 0
        for state in hmm: 
            geom=self.geometry_of_state(state)            
            if not geom:
                unlocated_states.append(state)
            else:
                ((lat1,lon1),(lat2,lon2))=geom
                state_spatial_index.insert(id,
                                           (min(lon1, lon2), min(lat1, lat2), 
                                            max(lon1, lon2), max(lat1, lat2)))
                id_to_state[id]=state
                id=id+1
            
        def candidate_states(obs): #was (lat,lon) in place of obs 
            geom = self.geometry_of_observation(obs)
            if geom == None:
                return hmm.keys()
            else:
                (lat,lon)=geom
                nearby_states = state_spatial_index.intersection((lon-MAX_DIST/METERS_PER_DEGREE_LONGITUDE,
                                                                  lat-MAX_DIST/METERS_PER_DEGREE_LATITUDE,
                                                                  lon+MAX_DIST/METERS_PER_DEGREE_LONGITUDE,
                                                                  lat+MAX_DIST/METERS_PER_DEGREE_LATITUDE))

                candidates = [id_to_state[id] for id in nearby_states]+unlocated_states
                return candidates

        self.viterbi = Viterbi(hmm,emission_probability,
                               constraint_length=constraint_length,
                               priors=priors,
                               candidate_states=candidate_states,
                               smallV=smallV)

    def step(self,obs,V,p):    
        if self.previous_obs != None:
            for int_obs in self.interpolated_obs(self.previous_obs, obs):
                V,p = self.viterbi.step(int_obs,V,p)        
        V,p = self.viterbi.step(obs,V,p)
        self.previous_obs = obs
        return V,p

    def interpolated_obs(self,prev,obs):
        return []

    def geometry_of_observation(self, obs):
        return obs

    def geometry_of_state(self, state):
        """ Subclasses should override this method to return the geometry of a given state, typically an edge."""
        if state == 'unknown': return None
        else:
            return state
