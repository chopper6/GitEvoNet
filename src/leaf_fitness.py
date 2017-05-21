import math

def node_score (leaf_metric, B, D):
    if (B+D==0): return 0

    if (leaf_metric=='RGAR'):
        if (B==0 and D > 0 or D==0 and B > 0): return 1
        else: return 0
    elif (leaf_metric=='ratio'): return max(B,D)/(B+D)
    elif (leaf_metric == 'one sided ratio'): return B/(B+D)
    elif (leaf_metric == 'ratio sq'): return math.pow(max(B,D)/(B+D),2)
    elif (leaf_metric == 'ratio btm sq'): return max(B,D)/math.pow((B+D),2)

    elif (leaf_metric == 'ratio 11'): return math.pow(B-D,2)
    elif (leaf_metric == 'dual 1'): return math.pow(B - D, 2) / (B + D)
    elif (leaf_metric == 'RGmG'):
        if (B==0 and D > 0 or D==0 and B > 0): return 1 #GREEN|RED
        if (D != 0):
            slice = round((float(B)/float(B+D))*100, 12)
            if (slice < 55 and slice > 45): return -1 #GREY
        return 0

    #NEW
    elif (leaf_metric == 'grey45'):
        if (B+D != 0):
            slice = round((float(B)/float(B+D))*100, 12)
            if (slice < 55 and slice > 45): return -1 #GREY
        return 0
    elif (leaf_metric == 'grey30'):
        if (B+D != 0):
            slice = round((float(B)/float(B+D))*100, 12)
            if (slice < 70 and slice > 30): return -1 #GREY
        return 0
    elif (leaf_metric == 'grey10'):
        if (B+D != 0):
            slice = round((float(B)/float(B+D))*100, 12)
            if (slice < 90 and slice > 10): return -1 #GREY
        return 0

    elif (leaf_metric == 'old1'):
        if (B+D == 0): return 0
        return abs(B-D)/(B+D)
    elif (leaf_metric == 'old2'):
        if (B+D == 0): return 0
        return math.pow(B-D,2)/(B+D)

    elif (leaf_metric == 'expo1'):
        if (B+D == 0): return 0
        return math.pow(2,abs(B-D)/float(B+D))

    elif (leaf_metric == 'ln1'):
        if (B+D==0 or B-D==0): return 0
        return math.log((abs(B-D)/float(B+D)))

    elif (leaf_metric == 'ln2'):
        if (B+D==0): return 0
        return math.log(100*(max(B,D)/float(B+D)))

    elif (leaf_metric == 'ln'):
        if (B+D==0): return 0
        return 1+math.log(max(B,D)/float(B+D))

    elif (leaf_metric == 'exp'):
        if (B+D == 0): return 0
        return math.pow(math.e,max(B,D)/float(B+D))

    elif (leaf_metric == 'log10'):
        if (B+D==0): return 0
        return math.log10(max(B,D)/float(B+D))

    elif (leaf_metric == 'sqrt1'):
        if (B+D==0): return 0
        return math.pow(abs(B-D)/float(B+D),.5)

    elif (leaf_metric == 'sqrt2'):
        if (B+D==0): return 0
        return math.pow(max(B,D)/float(B+D),.5)

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
        if (B+D==0): return 0
        if (B==0): H_B = 0
        else: H_B = -1*(B/(B+D)) * math.log2(B/(B+D))

        if (D==0): H_D = 0
        else: H_D = -1*(D/(B+D)) * math.log2(D/(B+D))

        return (H_B + H_D)


    else: print("ERROR in fitness.node_leaf_score(): unknown leaf metric: " + str(leaf_metric))


def assign_denom(leaf_metric, num_genes):
    #if (leaf_metric == 'ratio 11'): return math.pow(combo_sum,2)

    return num_genes

