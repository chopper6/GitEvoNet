import numpy as np

def node_score (hub_metric, B, D, soln_bens):
    # ASSUMES HUB IN SOLUTION
    if (B not in soln_bens): return 0

    freq = np.bincount(np.array(soln_bens))  

    if (hub_metric == 'ETB'): #also for ETG
        if (freq[B]==0): return 0
        return (B/freq[B])
    elif (hub_metric == 'control'):
        if (B == max(soln_bens)): return 1
        else: return 0
    else: return 1 #print("ERROR in fitness.node_hub_score(): unknown hub metric.")


def assign_numer (hub_metric, soln_bens, soln_dmgs):
    if (sum(soln_bens) == 0): return 0

    if (hub_metric=='ETB'): return sum(set(soln_bens))
    elif(hub_metric=='control'): return max(soln_bens)
    elif(hub_metric == 'Bin'): return sum(soln_bens)

    else: print("ERROR in fitness.assign_hub_numer(): unknown hub metric " + str(hub_metric))


def assign_denom (hub_metric, soln_bens):
    if (sum(soln_bens) == 0): return 1

    if (hub_metric=='ETB'): return 1 #sum(soln_bens)
    elif(hub_metric=='control'): return sum(soln_bens)

    #other poss include (sum(all_ben)) and len(soln_bens)

    else: return 1