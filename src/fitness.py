import math, random
from operator import attrgetter
import networkx as nx

def eval_fitness(population):
    #determines fitness of each individual and orders the population by fitness
    for p in range(len(population)):
        population[p].fitness = population[p].fitness_parts[2]
    population = sorted(population,key=attrgetter('fitness'), reverse=True)
    #reverse since MAX fitness function
    return population


def kp_instance_properties(a_result, leaf_metric, hub_metric, fitness_operator, net):

    #LEAF MEASURES
    RGAllR, ratio, ratio_onesided, ratio_sq, ratio_btm_sq, leaf_control = 0,0,0,0,0,0

    #HUB MEASURES
    ETB, ETBv2, ETBv2_insack, dist, dist_sq, effic, effic2 = 0,0,0,0,0,0,0
    all_ben = []
    soln_size = 1
    solver_time = 0

    if len(a_result) > 0:
        # -------------------------------------------------------------------------------------------------
        GENES_in, ALL_GENES, num_green, num_red, num_grey, solver_time = a_result[0], a_result[1], a_result[2], a_result[3], a_result[4], a_result[5]
        # -------------------------------------------------------------------------------------------------
        soln_bens = []
        soln_bens_sq = []
        soln_size = len(GENES_in)
        deg_dict, sack_dict = {},{}

        for g in GENES_in:
            B,D=g[1],g[2]
            soln_bens.append(B)
            soln_bens_sq.append(math.pow(B,2))

            deg = B+D #ASSUMES 100% PRESSURE

            if deg in sack_dict:
                sack_dict[deg][0] += 1
                sack_dict[deg][1] += B
            else:
                sack_dict[deg] = [1,B]

            

        for g in ALL_GENES:
            # g[0] gene name, g[1] benefits, g[2] damages, g[3] if in knapsack (binary)
            # hub score eval pt1
            B,D=g[1],g[2]
            deg = B+D #ASSUMES 100% PRESSURE
            if (B+D < 2): leaf_control += 1

            if deg in deg_dict:
                deg_dict[deg][0] += 1
                deg_dict[deg][1] += B
            else:
                deg_dict[deg] = [1,B]

            if (B + D != 0): 
                ratio_onesided += B/(B+D)
                ratio += max(B,D)/(B+D)
                ratio_sq += math.pow(max(B,D)/(B+D),2)
                ratio_btm_sq += max(B,D)/math.pow((B+D),2)

            dist +=  abs(B-D)
            dist_sq += math.pow(B-D,2)
            all_ben.append(B)

        max_ben = max(all_ben)
        num_genes = len(ALL_GENES)
        ETB = sum(set(soln_bens))
        if (sum(soln_bens) != 0):
            effic = math.pow(sum(soln_bens_sq),.5)/sum(soln_bens)
            effic2 = sum(soln_bens_sq)/math.pow(sum(soln_bens),2)
        else:
            effic = effic2 = 0
 
        for deg_set in deg_dict:
            ETBv2 += deg_dict[deg_set][1]/deg_dict[deg_set][0]

        for deg_set in sack_dict:
            ETBv2 += sack_dict[deg_set][1]/sack_dict[deg_set][0]
        #ETBv2 /= len(deg_dict) #is further normz nec?

        RGAllR = (num_green + num_red) / (num_green + num_red + num_grey)

        ratio_onesided /= num_genes
        ratio /= num_genes
        ratio_sq /= num_genes
        ratio_btm_sq /= num_genes
        leaf_control /= num_genes

        leaf_score = pick_leaf (leaf_metric, RGAllR, ratio, ratio_onesided, ratio_sq, ratio_btm_sq, leaf_control)
        hub_score = pick_hub (hub_metric, ETB, ETBv2, ETBv2_insack, dist, dist_sq, effic, effic2, max_ben)
        fitness_score = operate_on_features (leaf_score, hub_score, fitness_operator)

    else:
        print("WARNING in pressurize: no results from oracle advice")
        fitness_score = 0


    return [RGAllR, ETB, fitness_score]


def pick_leaf (leaf_metric, RGAllR, ratio, ratio_onesided, ratio_sq, ratio_btm_sq, leaf_control):
    if (leaf_metric=='RGAR'): return RGAllR
    elif (leaf_metric=='ratio'): return ratio
    elif (leaf_metric == 'one sided ratio'): return ratio_onesided
    elif (leaf_metric == 'ratio sq'): return ratio_sq
    elif (leaf_metric == 'ratio btm sq'): return ratio_btm_sq
    elif (leaf_metric == 'control'): return leaf_control
    else: print("ERROR in fitness.pick_leaf(): unknown leaf metric.")


def pick_hub (hub_metric, ETB, ETBv2, ETBv2_insack, dist, dist_sq, effic, effic2, max_ben):
    if (hub_metric=='ETB'): return ETB
    elif (hub_metric=='ETBv2'): return ETBv2
    elif (hub_metric=='ETBv2 in solution'): return ETBv2_insack
    elif(hub_metric=='dist'): return dist
    elif(hub_metric=='dist sq'): return dist_sq
    elif(hub_metric=='efficiency'): return effic
    elif(hub_metric=='efficiency 2'): return effic2
    elif(hub_metric=='control'): return max_ben
    else: print("ERROR in fitness.pick_hub(): unknown hub metric.")

def operate_on_features (leaf_score, hub_score, fitness_operator):
    if (fitness_operator=='leaf'): return leaf_score
    elif (fitness_operator=='hub'): return hub_score
    elif (fitness_operator=='add'): return leaf_score+hub_score
    elif (fitness_operator=='multiply'): return leaf_score*hub_score
    elif (fitness_operator=='power'): return math.pow(hub_score,leaf_score)
    else: print("ERROR in fitness.operate_on_features(): unknown fitness operator.")
