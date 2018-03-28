import math

def node_score (leaf_metric, B, D):
    if (B+D==0): return 0

    if (leaf_metric=='RGAR'):
        if (B==0 and D > 0 or D==0 and B > 0): return 1
        else: return 0

    elif (leaf_metric == 'info'): #used to be max_min_entropy, then capacity, then entropy prod
        #if (B+D==0): return 0
        if (B==0): H_B = 0
        else: H_B = -1*(B/(B+D)) * math.log2(B/(B+D))

        if (D==0): H_D = 0
        else: H_D = -1*(D/(B+D)) * math.log2(D/(B+D))

        return 1-(H_B + H_D)


    else: print("ERROR in fitness.node_leaf_score(): unknown leaf metric: " + str(leaf_metric))


def directed_node_score(leaf_metric, Bin, Bout, Din, Dout):
    # currently experimenting with this

    if (leaf_metric == 'entropy_conserved'):

        Bs = [Bin,Bout]
        Ds = [Din, Dout]
        S = [0,0] #ENTROPY [in,out[
        for i in range(2):
            B,D = Bs[i],Ds[i]

            if (B==0): H_B = 0
            else: H_B = -1*(B/(B+D)) * math.log(B/float(B+D),2)

            if (D==0): H_D = 0
            else: H_D = -1*(D/(B+D)) * math.log(D/float(B+D),2)

            S[i] = H_B + H_D

        Sin, Sout = S[0], S[1]

        return abs(Sin - Sout)


    elif (leaf_metric == 'mutual_info'):

        Bs = [Bin,Bout]
        Ds = [Din, Dout]
        S = [0,0] #ENTROPY [in,out]
        for i in range(2):
            B,D = Bs[i],Ds[i]
            S[i] = shannon_entropy(B,D)
        Sin, Sout = S[0], S[1]

        tot = (Bs[0]+Ds[0])*(Bs[1]+Ds[1])
        if tot==0: Sboth = 0
        else:
            pr11 = Bs[0]*Bs[1]/tot
            pr10 = Bs[0]*Ds[1]/tot
            pr01 = Ds[0]*Bs[1]/tot
            pr00 = Ds[0]*Ds[1]/tot

            assert(pr11+pr10+pr01+pr00 < 1.2 and pr11+pr10+pr01+pr00 > .8) #leave room for rounding

            if pr11==0: H11 = 0
            else: H11 = -1 * pr11 * math.log(pr11, 2)
            if pr10==0: H10 = 0
            else: H10 = -1 * pr10 * math.log(pr10, 2)
            if pr01==0: H01 = 0
            else: H01 = -1 * pr01 * math.log(pr01, 2)
            if pr00==0: H00 = 0
            else: H00 = -1 * pr00 * math.log(pr00, 2)
            Sboth = H11+H10+H01+H00
        assert(Sboth >= 0 and Sboth <= 2)

        assert(Sin+Sout-Sboth >= -.2 and Sin+Sout-Sboth <= 1.2) #room for rounding
        return Sin+Sout-Sboth


    elif (leaf_metric == 'mutual_info_rev'):

        Bs = [Bin,Bout]
        Ds = [Din, Dout]
        S = [0,0] #ENTROPY [in,out]
        for i in range(2):
            B,D = Bs[i],Ds[i]
            S[i] = shannon_entropy(B,D)
        Sin, Sout = S[0], S[1]

        tot = (Bs[0]+Ds[0])*(Bs[1]+Ds[1])
        if tot == 0: Sboth = 0
        else:
            pr11 = Bs[0]*Bs[1]/tot
            pr10 = Bs[0]*Ds[1]/tot
            pr01 = Ds[0]*Bs[1]/tot
            pr00 = Ds[0]*Ds[1]/tot

            assert(pr11+pr10+pr01+pr00 < 1.2 and pr11+pr10+pr01+pr00 > .8) #leave room for rounding

            if pr11==0: H11 = 0
            else: H11 = -1 * pr11 * math.log(pr11, 2)
            if pr10==0: H10 = 0
            else: H10 = -1 * pr10 * math.log(pr10, 2)
            if pr01==0: H01 = 0
            else: H01 = -1 * pr01 * math.log(pr01, 2)
            if pr00==0: H00 = 0
            else: H00 = -1 * pr00 * math.log(pr00, 2)
            Sboth = H11+H10+H01+H00
        assert(Sboth >= 0 and Sboth <= 2)

        assert(1-Sin+Sout-Sboth >= -.2 and 1-Sin+Sout-Sboth <= 1.2)
        return 1-Sin+Sout-Sboth


    else: print("ERROR in fitness.node_leaf_score(): unknown leaf metric: " + str(leaf_metric))


def shannon_entropy(B,D):
    if (B == 0): H_B = 0
    else: H_B = -1 * (B / (B + D)) * math.log(B / float(B + D), 2)

    if (D == 0):  H_D = 0
    else:  H_D = -1 * (D / (B + D)) * math.log(D / float(B + D), 2)

    return H_B + H_D
