import math

def node_score (leaf_metric, B, D):
    if (B+D==0): return 0

    if (leaf_metric=='RGAR'):
        if (B==0 and D > 0 or D==0 and B > 0): return 1
        else: return 0

    elif (leaf_metric == 'unambig'):
        if (B+D==0): return 0
        val = .5**B * .5**D

    elif (leaf_metric == 'combo'):
        return (math.factorial(B)*math.factorial(D)/float(math.factorial(B+D)))

    elif (leaf_metric == 'combo2'):
        return (math.factorial(B+D)/float(math.factorial(B)*math.factorial(D)))

    elif (leaf_metric == 'entropy1'):
        return ((B+D+1)*math.factorial(B)*math.factorial(D)/float(math.factorial(B+D)))

    elif (leaf_metric == 'entropy2'):
        return (math.factorial(B+D)/float(math.factorial(B)*math.factorial(D)))

    elif (leaf_metric == 'entropy3'):
        return (math.pow(2,(B+D))*math.factorial(B)*math.factorial(D)/float(math.factorial(B+D)))    

    elif (leaf_metric == 'entropy4'):
        return (math.pow(2,(B+D)) - (math.factorial(B+D)/float(math.factorial(B)*math.factorial(D))))/ math.pow(2,(B+D))

    elif (leaf_metric == 'entropy5'):
        return (math.factorial(B+D)/float(math.factorial(B)*math.factorial(D)))

    elif (leaf_metric == 'entropy7'):
        return math.log(math.factorial(B+D)/float(math.factorial(B)*math.factorial(D)),2)

    elif (leaf_metric == 'shannon'):
        if (B+D==0): return 0
        if (B==0): H_B = 0
        else: H_B = -1*(B/(B+D)) * math.log2(B/(B+D))

        if (D==0): H_D = 0
        else: H_D = -1*(D/(B+D)) * math.log2(D/(B+D))

        if (H_B + H_D == 0): print("0 at B= " + str(B) + ", D= " + str(D))
        
        if (H_B + H_D != 0): return (H_B + H_D)
        else: return 1

    elif (leaf_metric == 'shannon2'):
        if (B+D==0): return 0
        if (B==0): H_B = 0
        else: H_B = -1*(B/(B+D)) * math.log2(B/(B+D))

        if (D==0): H_D = 0
        else: H_D = -1*(D/(B+D)) * math.log2(D/(B+D))

        if (H_B + H_D == 0): print("0 at B= " + str(B) + ", D= " + str(D))

        if (1 - (H_B + H_D) != 0): return (1 - (H_B + H_D))
        else: return 1


    elif (leaf_metric == 'shannon3'):
        if (B+D==0): return 0
        if (B==0): H_B = 0
        else: H_B = -1*(B/(B+D)) * math.log2(B/(B+D))

        if (D==0): H_D = 0
        else: H_D = -1*(D/(B+D)) * math.log2(D/(B+D))

        return 2 - (H_B + H_D)

    elif (leaf_metric == 'log_shannon3'):
        if (B+D==0): return 0
        if (B==0): H_B = 0
        else: H_B = -1*(B/(B+D)) * math.log2(B/(B+D))

        if (D==0): H_D = 0
        else: H_D = -1*(D/(B+D)) * math.log2(D/(B+D))

        return math.log2(2 - (H_B + H_D))

    elif (leaf_metric == 'loglog_shannon3'):
        if (B+D==0): return 0
        if (B==0): H_B = 0
        else: H_B = -1*(B/(B+D)) * math.log2(B/(B+D))

        if (D==0): H_D = 0
        else: H_D = -1*(D/(B+D)) * math.log2(D/(B+D))

        Hmin = 2 - (H_B + H_D)
        return Hmin*math.log2(Hmin)



    elif (leaf_metric == 'shannon4'):
        if (B+D==0): return 0
        if (B==0): H_B = 0
        else: H_B = -1*(B/(B+D)) * math.log2(B/(B+D))

        if (D==0): H_D = 0
        else: H_D = -1*(D/(B+D)) * math.log2(D/(B+D))

        return 1 - (H_B + H_D)

    elif (leaf_metric == 'shannon5'):
        if (B+D==0): return 0
        if (B==0): H_B = 0
        else: H_B = -1*(B/(B+D)) * math.log2(B/(B+D))

        if (D==0): H_D = 0
        else: H_D = -1*(D/(B+D)) * math.log2(D/(B+D))

        H = 1 - (H_B + H_D)
        return math.pow(2,H)

    elif (leaf_metric == "double_ratioSq"):
        if (B+D) == 0: return 0
        else:
            return ((.0625-math.pow(B/(B+D),2)*math.pow(D/(B+D),2)))*16

    elif (leaf_metric == "double_ratio"):
        if (B+D) == 0: return 0
        else:
            return (.25-(math.pow(B/(B+D),1)*math.pow(D/(B+D),1)))*4



    # MIN ENTROPY
    elif (leaf_metric == 'min_entropy'):
        #if (B+D==0): return 0
        if (B+D == 0): prB=prD=0
        else:
            prB = B/float(B+D)
            prD = D/float(B+D)
        try: assert(B+D == 1 and B>=0 and D>=0)
        except: print("ERROR in leaf fitness: B=" + str(B) + ", D=" + str(D))

        if (prB==0): H_B = 0
        else: H_B = -1*prB * math.log2(prB)

        if (prD==0): H_D = 0
        else: H_D = -1*prD * math.log2(prD)

        min_entropy = max(H_B+H_D, .0000000000000000000000001)
        return min_entropy

    elif (leaf_metric == 'entropy_prod'): #used to be max_min_entropy or capacity
        #if (B+D==0): return 0
        if (B==0): H_B = 0
        else: H_B = -1*(B/(B+D)) * math.log2(B/(B+D))

        if (D==0): H_D = 0
        else: H_D = -1*(D/(B+D)) * math.log2(D/(B+D))

        return 1-(H_B + H_D)

    elif (leaf_metric == 'entropy'):
        if (B==0): H_B = 0
        else: H_B = -1*(B/(B+D)) * math.log(B/float(B+D),2)

        if (D==0): H_D = 0
        else: H_D = -1*(D/(B+D)) * math.log(D/float(B+D),2)

        if (B+D==0): return 0
        else: return math.pow(2,(H_B + H_D))

    elif (leaf_metric == 'negentropy'):
        if (B==0): H_B = 0
        else: H_B = -1*(B/(B+D)) * math.log(B/float(B+D),2)

        if (D==0): H_D = 0
        else: H_D = -1*(D/(B+D)) * math.log(D/float(B+D),2)

        if (B+D==0): return 0
        else: return -(H_B + H_D)




    else: print("ERROR in fitness.node_leaf_score(): unknown leaf metric: " + str(leaf_metric))

def directed_node_score(leaf_metric, Bin, Bout, Din, Dout):

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


def assign_denom(leaf_metric, num_genes):
    #if (leaf_metric == 'ratio 11'): return math.pow(combo_sum,2)

    return num_genes

def shannon_entropy(B,D):
    if (B == 0): H_B = 0
    else: H_B = -1 * (B / (B + D)) * math.log(B / float(B + D), 2)

    if (D == 0):  H_D = 0
    else:  H_D = -1 * (D / (B + D)) * math.log(D / float(B + D), 2)

    return H_B + H_D
