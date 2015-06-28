import math
import datetime
import time
import sys
import collections

class Viterbi:    
    def __init__(self, hmm, emission_probability, priors=None, constraint_length=10, candidate_states=None, smallV=0.00000000001):
        """ Sets the stage for running the viterbi algorithm.
        hmm -- a map { state_id : [(next_state1, probability), (next_state2, probability)]}
        priors -- a map { state_id : probability } where the sum of probabilities=1
        emission_probability -- a function(state_id, observation) -> [0..1]
        constraint_length -- how many steps into the past to consider
        candidate_states -- a function f(obs) that returns a set of state ids given an observation

        """
        self.hmm = hmm;
        
        self.emission_probability = emission_probability;
        self.constraint_length = constraint_length;        
        if(candidate_states):
            self.candidate_states = candidate_states
        else:
            self.candidate_states = lambda obs: self.hmm.keys()
            
        if not priors:
            self.priors = {}
            for state in self.hmm:
                self.priors[state]=1.0/len(self.hmm)
        else:
            self.priors = priors

        # set up the 'incoming' reverse index: for each state, what states contribute to its probability?
        self.incoming = {}
        
        for from_state in hmm:
            for to_state, probability in hmm[from_state]:                
                if not to_state in self.incoming:
                    self.incoming[to_state]={}
                self.incoming[to_state][from_state] = probability
        
        self.smallV = smallV

    def step(self, obs, V=None, path={}):
        """ performs viterbi matching. updates matrix V based on a single observation """

        # if no priors are specified, make them uniform 
        if V == None:
            V=dict(self.priors)
        newV = {}
        newPath = {}

        # states that the current observation could in some way support
        state_eps =  map(lambda state: (state, self.emission_probability(state, obs)), self.candidate_states(obs))
        nonzero_eps = filter(lambda (state, ep): ep>0, state_eps)

        # for each candidate state, calculate its maximum probability path
        for to_state, emission_probability in nonzero_eps:
            
            # some states may have millions of incoming edges
            if len(self.incoming[to_state]) < len(V):
                nonzero_incoming = filter(lambda (from_state, probability): from_state in V and V[from_state]>0, self.incoming[to_state].iteritems())
            else:
                nonzero_incoming_without_p = filter(lambda from_state: from_state in self.incoming[to_state], V)
                nonzero_incoming = map(lambda from_state: (from_state, self.incoming[to_state][from_state]), nonzero_incoming_without_p)
            
            # list of previous possible states and their probabilities (prob, state)
            from_probs = map(lambda (from_state, transition_probability): 
                               (V[from_state]*emission_probability*transition_probability, from_state),
                               nonzero_incoming)
            
            if len(from_probs) > 0:
                (max_prob,max_from) = max(from_probs)
                newV[to_state]=max_prob
                
                # make sure we don't grow paths beyond the constraint length
                if not max_from in path:
                    path[max_from]=[];
                if len(path[max_from]) == self.constraint_length:
                    path[max_from].pop(0)                    
                        
                newPath[to_state] = path[max_from] + [to_state]
        
        newV=self.normalize(newV)
        
        small = filter(lambda x: newV[x] < self.smallV, newV)
        for state in small:
            del newV[state]
            # jakob: this seems iffy, there should be no V for which there is no path
            if state in newPath:
                del newPath[state]

        return newV, newPath

        
    def normalize(self,V):
        """ normalizes viterbi matrix V, so that the sum of probabilities add up to 1 """
        sumProb = sum(V.values())
        
        # if we're stuck with no probability mass, return to priors instead
        if sumProb == 0: 
            return dict(self.priors)

        ret=dict([(state, V[state]/sumProb) for state in V])
        return ret
		
