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
    elif (hub_metric == 'effic .5'): return math.pow(B,.5)
    elif (hub_metric == 'control'):
        if (B == max(soln_bens)): return 1
        else: return 0
    else: return 1 #print("ERROR in fitness.node_hub_score(): unknown hub metric.")


def assign_numer (hub_metric, soln_bens, soln_dmgs, soln_bens_sq, soln_bens_4):
    if (sum(soln_bens) == 0): return 0

    if (hub_metric=='ETB'): return sum(set(soln_bens))
    elif (hub_metric=='multETB'):
        numer = 1
        for B in set(soln_bens):
            numer *= B
        return numer
    elif (hub_metric == 'ETB sqrt'): return math.pow(sum(set(soln_bens)),.5)
    elif(hub_metric=='effic'): return math.pow(sum(soln_bens_sq), .5)
    elif(hub_metric=='effic 2'): return sum(soln_bens_sq)
    elif(hub_metric=='effic 4'): return sum(soln_bens_4)
    elif(hub_metric=='effic 8'): 
        numer=0
        for B in soln_bens:
            numer += math.pow(B,8)
        return numer

    elif (hub_metric == 'effic sqrt'): 
        soln_rt = 0
        for B in soln_bens:
            soln_rt += math.pow(B,.5)
        return soln_rt
    elif (hub_metric == 'Bsq'): return sum(soln_bens_sq)
    elif (hub_metric == 'multB'):
        numer = 1
        for B in soln_bens:
            numer *= B
        return numer

    elif(hub_metric=='control'): return max(soln_bens)

    elif (hub_metric=='ratio'):
        numer=1
        for i in range(len(soln_bens)):
            B = soln_bens[i]
            D = soln_dmgs[i]
            numer *= B/float(B+D)
        return numer

    elif (hub_metric=='combo'):
        numer=0
        for i in range(len(soln_bens)):
            B = soln_bens[i]
            D = soln_dmgs[i]
            numer += (math.factorial(B)*math.factorial(D)/float(math.factorial(B+D)))
        return numer

    elif (hub_metric=='combo prod'):
        numer=1
        for i in range(len(soln_bens)):
            B = soln_bens[i]
            D = soln_dmgs[i]
            numer *= (math.factorial(B)*math.factorial(D)/float(math.factorial(B+D)))
        return numer

    #NEW
    elif(hub_metric=='1'):
        powB = 0
        for B in soln_bens:
            powB += math.pow(B,2)
        return powB

    elif(hub_metric=='2'):
        powB = 0
        for B in soln_bens:
            powB += math.pow(B,10)
        return powB

    elif(hub_metric=='3'):
        powB = 0
        for B in soln_bens:
            powB *= math.pow(B,2)
        return powB

    elif(hub_metric=='ln'):
        
        return -1*math.log(sum(soln_bens))


    else: print("ERROR in fitness.assign_hub_numer(): unknown hub metric.")


def assign_denom (hub_metric, soln_bens):
    if (sum(soln_bens) == 0): return 1

    if (hub_metric=='ETB' or hub_metric=='multETB' or hub_metric=='multB' or hub_metric=='Bsq' or hub_metric=='combo' or hub_metric=='combo prod'): return 1 #sum(soln_bens)
    elif (hub_metric == 'ETB sqrt'): return math.pow(sum(soln_bens), .5)
    elif(hub_metric=='effic'): return sum(soln_bens)
    elif(hub_metric=='effic 2'): return math.pow(sum(soln_bens), 2)
    elif(hub_metric=='effic 4'): return math.pow(sum(soln_bens), 4)
    elif(hub_metric=='effic 8'): return math.pow(sum(soln_bens), 8)
    elif(hub_metric == 'effic sqrt'): return math.pow(sum(soln_bens), .5)
    elif(hub_metric=='control'): return sum(soln_bens)
    elif(hub_metric=='ratio'): return 1

    #NEW
    elif (hub_metric == '1'):
        return math.pow(2,sum(soln_bens))

    elif (hub_metric == '2'):
        return math.pow(10,sum(soln_bens))

    elif (hub_metric == '3'):
        powB = 0
        for B in soln_bens:
            powB *= B
        return math.pow(2,powB)

    elif(hub_metric=='ln'):
        logB = 0
        for B in soln_bens:
            logB += math.log(B)
        return logB

    else: print("ERROR in fitness.assign_hub_denom(): unknown hub metric:" + str(hub_metric))
