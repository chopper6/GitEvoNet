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
        return math.log(100*(abs(B-D)/float(B+D)))

    elif (leaf_metric == 'ln2'):
        if (B+D==0): return 0
        return math.log(100*(max(B,D)/float(B+D)))

    elif (leaf_metric == 'sqrt1'):
        if (B+D==0): return 0
        return math.pow(abs(B-D)/float(B+D),.5)

    elif (leaf_metric == 'sqrt2'):
        if (B+D==0): return 0
        return math.pow(max(B,D)/float(B+D),.5)

    else: print("ERROR in fitness.node_leaf_score(): unknown leaf metric: " + str(leaf_metric))


def assign_denom(leaf_metric, num_genes):
    #if (leaf_metric == 'ratio 11'): return math.pow(combo_sum,2)
    return num_genes

