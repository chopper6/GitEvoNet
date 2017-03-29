import math
import numpy as np

def node_score (hub_metric, B, D, soln_bens):
    # ASSUMES HUB IN SOLUTION
    if (B not in soln_bens): return 0

    freq = np.bincount(np.array(soln_bens))  

    if (hub_metric == 'ETB'): 
        if (freq[B]==0): return 0
        return (B/freq[B])
    elif (hub_metric == 'effic'): return math.pow(B,2) #no good way to capture
    elif (hub_metric == 'effic 2'): return math.pow(B,2)
    elif (hub_metric == 'effic 4'): return math.pow(B,4)
    elif (hub_metric == 'control'):
        if (B == max(soln_bens)): return 1
        else: return 0
    else: print("ERROR in fitness.node_hub_score(): unknown hub metric.")


def assign_numer (hub_metric, soln_bens, soln_bens_sq, soln_bens_4):
    if (sum(soln_bens) == 0): return 0

    if (hub_metric=='ETB'): return math.pow(sum(set(soln_bens)),2)
    elif(hub_metric=='effic'): return math.pow(sum(soln_bens_sq), .5)
    elif(hub_metric=='effic 2'): return sum(soln_bens_sq)
    elif(hub_metric=='effic 4'): return sum(soln_bens_4)
    elif(hub_metric=='control'): return max(soln_bens)
    else: print("ERROR in fitness.assign_hub_numer(): unknown hub metric.")


def assign_denom (hub_metric, soln_bens):
    if (sum(soln_bens) == 0): return 1

    if (hub_metric=='ETB'): return sum(soln_bens)
    elif(hub_metric=='effic'): return sum(soln_bens)
    elif(hub_metric=='effic 2'): return math.pow(sum(soln_bens), 2)
    elif(hub_metric=='effic 4'): return math.pow(sum(soln_bens), 4)
    elif(hub_metric=='control'): return sum(soln_bens)
    else: print("ERROR in fitness.assign_hub_denom(): unknown hub metric.")
