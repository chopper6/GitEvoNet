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
    elif (leaf_metric == 'RGMG'):
        if (B==0 and D > 0 or D==0 and B > 0): return 1
        else: return -1
    else: print("ERROR in fitness.node_leaf_score(): unknown leaf metric.")


def assign_denom(leaf_metric, num_genes):
    #if (leaf_metric == 'ratio 11'): return math.pow(combo_sum,2)
    return num_genes

