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

    if (hub_metric=='ETB' or hub_metric=='old ETB'): return sum(set(soln_bens))
    elif(hub_metric == 'ETB RG'):
        numer=0
        for i in range(len(soln_bens)):
            if (soln_dmgs[i] == 0): numer += 1
        RG = numer / len(soln_bens)
        return RG*sum(set(soln_bens))

    elif(hub_metric == 'ETB combo'):
        numer=0
        for i in range(len(soln_bens)):
            B = soln_bens[i]
            D = soln_dmgs[i]
            numer += (math.factorial(B)*math.factorial(D)/float(math.factorial(B+D)))
        return numer*sum(set(soln_bens))

    elif(hub_metric == 'ETB combo sq'):
        numer=0
        for i in range(len(soln_bens)):
            B = soln_bens[i]
            D = soln_dmgs[i]
            numer += (math.factorial(B)*math.factorial(D)/float(math.factorial(B+D)))
        return math.pow(numer,2)*sum(set(soln_bens))


    elif (hub_metric=='multETB'):
        numer = 1
        for B in set(soln_bens):
            numer *= B
        return numer
    elif (hub_metric == 'ETBv2'): return sum(soln_bens)
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

    elif (hub_metric=='ln combo'):
        numer=0
        for i in range(len(soln_bens)):
            B = soln_bens[i]
            D = soln_dmgs[i]
            numer += math.log(math.factorial(B)*math.factorial(D)/float(math.factorial(B+D)),2)
        return numer

    elif (hub_metric=='combo prod'):
        numer=1
        for i in range(len(soln_bens)):
            B = soln_bens[i]
            D = soln_dmgs[i]
            numer *= (math.factorial(B)*math.factorial(D)/float(math.factorial(B+D)))
        return numer

    elif (hub_metric == 'entropy1'):
        numer=0
        for i in range(len(soln_bens)):
            B = soln_bens[i]
            D = soln_dmgs[i]
            numer += ((B+D+1)*math.factorial(B)*math.factorial(D)/float(math.factorial(B+D)))
        return numer

    elif (hub_metric == 'entropy2'):
        numer=0
        for i in range(len(soln_bens)):
            B = soln_bens[i]
            D = soln_dmgs[i]
            numer += (math.factorial(B+D)/float(math.factorial(B)*math.factorial(D)))
        return numer

    elif (hub_metric == 'entropy3'):
        numer=0
        for i in range(len(soln_bens)):
            B = soln_bens[i]
            D = soln_dmgs[i]
            numer +=  (math.pow(2,(B+D))*math.factorial(B)*math.factorial(D)/float(math.factorial(B+D)))
        return numer

    elif (hub_metric == 'entropy3 prod'):
        numer=1
        for i in range(len(soln_bens)):
            B = soln_bens[i]
            D = soln_dmgs[i]
            numer *=  (math.pow(2,(B+D))*math.factorial(B)*math.factorial(D)/float(math.factorial(B+D)))
        return numer


    elif (hub_metric == 'entropy4'):
        numer=0
        for i in range(len(soln_bens)):
            B = soln_bens[i]
            D = soln_dmgs[i]
            numer +=   (math.pow(2,(B+D)) - (math.factorial(B+D)/float(math.factorial(B)*math.factorial(D))))/math.pow(2,(B+D))
        return numer
    elif (hub_metric == 'entropy4 prod'):
        numer=1
        for i in range(len(soln_bens)):
            B = soln_bens[i]
            D = soln_dmgs[i]
            numer *=  (math.pow(2,(B+D)) - (math.factorial(B+D)/float(math.factorial(B)*math.factorial(D))))/math.pow(2,(B+D))
        return numer

    elif (hub_metric == 'ETB entropy4'):
        numer=0
        for i in range(len(soln_bens)):
            B = soln_bens[i]
            D = soln_dmgs[i]
            numer +=   (math.pow(2,(B+D)) - (math.factorial(B+D)/float(math.factorial(B)*math.factorial(D))))/math.pow(2,(B+D))
        return numer*sum(set(soln_bens))

    elif (hub_metric=='entropy5'):
        numer=0
        for i in range(len(soln_bens)):
            B = soln_bens[i]
            D = soln_dmgs[i]
            numer += (math.factorial(B+D)/float(math.factorial(D)*math.factorial(B)))
        return numer

    elif (hub_metric=='entropy5 prod'):
        numer=1
        for i in range(len(soln_bens)):
            B = soln_bens[i]
            D = soln_dmgs[i]
            numer *= (math.factorial(B+D)/float(math.factorial(D)*math.factorial(B)))
        return numer

    elif (hub_metric == 'entropy6'): #same as 4?
        entropy_after =0
        total_degs = 0
        for i in range(len(soln_bens)):
            B = soln_bens[i]
            D = soln_dmgs[i]
            entropy_after +=   (math.factorial(B+D)/float(math.factorial(B)*math.factorial(D)))
            total_degs += B+D
        entropy_before = math.pow(2,total_degs)
        return (entropy_before - entropy_after) / float(entropy_before)

    elif (hub_metric == 'entropy9'):
        entropy_after =0
        total_degs = 0
        for i in range(len(soln_bens)):
            B = soln_bens[i]
            D = soln_dmgs[i]
            entropy_after +=   (math.factorial(B+D)/float(math.factorial(B)*math.factorial(D)))
            total_degs += B+D-1
        entropy_before = math.pow(2,total_degs)
        return (entropy_before - entropy_after) / float(entropy_before)

    elif (hub_metric == 'entropy7'):
        numer=0
        for i in range(len(soln_bens)):
            B = soln_bens[i]
            D = soln_dmgs[i]
            numer += math.log(math.factorial(B+D)/float(math.factorial(B)*math.factorial(D)),2)
        return numer

    elif (hub_metric == 'entropy8'):
        numer=0
        for i in range(len(soln_bens)):
            B = soln_bens[i]
            D = soln_dmgs[i]
            numer +=   (math.pow(2,(B+D)) - (math.factorial(B+D)/float(math.factorial(B)*math.factorial(D))))
        return numer

    elif (hub_metric == 'sum shannon'):
        numer = 0
        for i in range(len(soln_bens)):
            B = soln_bens[i]
            D = soln_dmgs[i]
            if (B+D != 0): 
                if (B==0): H_B = 0
                else: H_B = -1*(B/(B+D)) * math.log2(B/(B+D))

                if (D==0): H_D = 0
                else: H_D = -1*(D/(B+D)) * math.log2(D/(B+D))

                numer += 2 - (H_B + H_D)

        return numer


    elif (hub_metric == 'prod shannon'):
        numer = 1
        for i in range(len(soln_bens)):
            B = soln_bens[i]
            D = soln_dmgs[i]
            if (B+D != 0):
                if (B==0): H_B = 0
                else: H_B = -1*(B/(B+D)) * math.log2(B/(B+D))

                if (D==0): H_D = 0
                else: H_D = -1*(D/(B+D)) * math.log2(D/(B+D))

                numer *= (2 - (H_B + H_D))

        return numer



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

    if (hub_metric=='ETB' or hub_metric=='ETBv2' or hub_metric=='multETB' or hub_metric=='multB' or hub_metric=='Bsq' or hub_metric=='combo' or hub_metric=='combo prod'): return 1 #sum(soln_bens)
    elif (hub_metric == 'ETB sqrt'): return math.pow(sum(soln_bens), .5)
    elif(hub_metric=='effic'): return sum(soln_bens)
    elif(hub_metric=='effic 2'): return math.pow(sum(soln_bens), 2)
    elif(hub_metric=='effic 4'): return math.pow(sum(soln_bens), 4)
    elif(hub_metric=='effic 8'): return math.pow(sum(soln_bens), 8)
    elif(hub_metric == 'effic sqrt'): return math.pow(sum(soln_bens), .5)
    elif(hub_metric=='control'): return sum(soln_bens)
    elif(hub_metric=='ratio'): return 1
    elif(hub_metric=='old ETB' or hub_metric=='ETB combo'): return sum(soln_bens)

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
    #TODO: for fucks sake just default to returning 1 
    else: return 1
    #elif (hub_metric == 'entropy1' or hub_metric == 'entropy2' or hub_metric == 'entropy3' or hub_metric == 'entropy4' or hub_metric == 'entropy4 prod' or hub_metric == 'entropy3 prod' or hub_metric == 'entropy5' or hub_metric == 'entropy5 prod' or hub_metric == 'entropy6' or hub_metric == 'ETB entropy4' or hub_metric == 'ETB RG' or hub_metric == 'entropy7' or hub_metric == 'ln combo' or hub_metric == 'entropy8' or hub_metric == 'entropy9' or hub_metric=='ETB combo sq'): return 1
    #else: print("ERROR in fitness.assign_hub_denom(): unknown hub metric:" + str(hub_metric))
