import math, random
from operator import attrgetter
import networkx as nx

def eval_fitness(population, fitness_type):
    #determines fitness of each individual and orders the population by fitness
    for p in range(len(population)):
        population[p].fitness = population[p].fitness_parts[2]
    population = sorted(population,key=attrgetter('fitness'), reverse=True)
    #reverse since MAX fitness function
    return population


def kp_instance_properties(a_result, fitness_type, node_fitness_type, net):
    #TODO: trim fitness calcs if know which ones to use

    RGGR, ETB, RGAllR, ben_ratio, ben, solver_time = 0,0,0,0,0,0
    ben_dmg, ben_dmg_sq, ben_sq = 0,0,0
    uncorr, uncorr_sq = 0,0
    all_ben, all_dmg, bendmg = 0,0,0
    grey=0
    grey_score = 0
    soln_size = 1
    effic = 0
    ratio2, ratio2_sq, ratio2_btm_sq = 0,0,0
    if len(a_result) > 0:
        # -------------------------------------------------------------------------------------------------
        GENES_in, GENES_out, num_green, num_red, num_grey, solver_time = a_result[0], a_result[1], a_result[2], a_result[3], a_result[4], a_result[5]
        # -------------------------------------------------------------------------------------------------
        soln_bens = []
        soln_size = len(GENES_in)
        for g in GENES_in:
            # g[0] gene name, g[1] benefits, g[2] damages, g[3] if in knapsack (binary)
            # hub score eval pt1
            B,D=g[1],g[2]
            id = int(g[0])
            
            if (D != 0): 
                if (B/D < 3/2 and B/D > 2/3): grey+=1

            ben += B
            ben_sq += math.pow(B,2)
            soln_bens.append(B)
            if (B + D != 0): 
                ben_ratio += B/(B+D)
                ratio2 += max(B,D)/(B+D)
                ratio2_sq += math.pow(max(B,D)/(B+D),2)
                ratio2_btm_sq += max(B,D)/math.pow((B+D),2)
            ben_dmg +=  abs(B-D)
            ben_dmg_sq += math.pow(B-D,2)
            
            if (B != 0 and D != 0):  
                uncorr += min(B/D, D/B)
                uncorr_sq += min(math.pow(B/D,2),math.pow(D/B,2))
            else: 
                uncorr += 0
                uncorr_sq += 0 
 
            all_ben += B
            all_dmg += D
            bendmg += B*D

            

            # NODE FITNESS inside soln
            if (node_fitness_type == 0):
                net.node[id]['fitness'] += abs(B-D)
            elif (node_fitness_type == 1):
                net.node[id]['fitness'] += math.pow(B-D,2)
            elif (node_fitness_type == 2):
                if (B != 0 and D != 0):  net.node[id]['fitness'] += 1-min(B/D, D/B)
                else: net.node[id]['fitness'] += 1


        for g in GENES_out:
            B,D=g[1],g[2]
            id = int(g[0])
            ben_dmg +=  abs(B-D)

            all_ben += B
            all_dmg += D
            bendmg += B*D
            ben_dmg_sq += math.pow(B-D,2)

            if (B + D != 0):
                ben_ratio += B/(B+D)
                ratio2 += max(B,D)/(B+D)
                ratio2_sq += math.pow(max(B,D)/(B+D),2)
                ratio2_btm_sq += max(B,D)/math.pow((B+D),2)

            if (D != 0):
                if (B/D < 3/2 and B/D > 2/3): grey+=1

            if (B != 0 and D != 0):
                uncorr += min(B/D, D/B)
                uncorr_sq += min(math.pow(B/D,2),math.pow(D/B,2))
            else:
                uncorr += 0
                uncorr_sq += 0

            # NODE FITNESS outside soln
            if (node_fitness_type == 0):
                net.node[id]['fitness'] += abs(B-D)
            elif (node_fitness_type == 1):
                net.node[id]['fitness'] += math.pow(B-D,2)
            elif (node_fitness_type == 2):
                if (B != 0 and D != 0):   net[id]['fitness'] += 1-min(B/D, D/B)
                else: net.node[id]['fitness']  += 1

        num_obj = len(GENES_in+GENES_out)
        ETB = sum(set(soln_bens))
        uncorr = 1-(uncorr/num_obj)
        uncorr_sq = 1-(uncorr_sq/num_obj)
        if (ben != 0): effic = math.pow(ben_sq,.5)/ben

        if (num_grey != 0):
            RGGR = (num_green + num_red) / num_grey
        else:
            RGGR = (num_green + num_red)
        RGAllR = (num_green + num_red) / (num_green + num_red + num_grey)

        grey_score = 1-grey/(len(GENES_in+GENES_out))

    else:
        print("WARNING in pressurize: no results from oracle advice")

    denom = math.pow(math.pow(all_ben,2)*math.pow(all_dmg,2),.5)
    if (denom != 0):  corr = (1-(bendmg /denom))
    else: corr=1

    if (fitness_type == 0):
        return [RGGR, ETB, RGAllR*ETB]
    elif (fitness_type == 1):
        return [RGGR, ETB, ben_ratio]
    elif (fitness_type == 2):
        return [RGGR, ETB, ben]
    elif (fitness_type == 3):
        return [RGGR, ETB, ben_dmg]
    elif (fitness_type == 4):
        return [RGAllR, ETB, ben*RGAllR]
    elif (fitness_type == 5):
        return [RGAllR, ETB, uncorr]
    elif (fitness_type == 6):
        return [RGAllR, ETB, random.random()]
    elif (fitness_type == 7):
        return [RGAllR, ETB, ETB]
    elif (fitness_type == 8):
        return [RGAllR, ETB, RGAllR]
    elif (fitness_type == 9):
        return [RGAllR, ETB, corr]
    elif (fitness_type == 10):
        return [RGGR, ETB, ben_dmg_sq]
    elif (fitness_type == 11):
        return [RGAllR, ETB, corr*ben_dmg_sq]
    elif (fitness_type == 12):
        return [RGAllR, ETB, RGAllR*ben_dmg_sq]
    elif (fitness_type == 13):
        return [RGAllR, ETB, grey_score*ETB]
    elif (fitness_type == 14):
        return [RGAllR, ETB, grey_score*ben_dmg_sq] 
    elif (fitness_type == 15):
        return [RGAllR, ETB, uncorr*ETB]
    elif (fitness_type == 16):
        return [RGAllR, ETB, uncorr*ben_dmg_sq]
    elif (fitness_type == 17):
        return [RGAllR, ETB, uncorr*ben/soln_size]
    elif (fitness_type == 18):
        return [RGAllR, ETB, uncorr*effic]
    elif (fitness_type == 19):
        return [RGAllR, ETB, grey_score*effic]


    elif (fitness_type == 20):
        return [RGAllR, ETB, math.pow(ETB,uncorr)]
    elif (fitness_type == 21):
        return [RGAllR, ETB, math.pow(ETB,grey_score)]
    elif (fitness_type == 22):
        return [RGAllR, ETB, uncorr_sq]
    elif (fitness_type == 23):
        return [RGAllR, ETB, grey_score]
    elif (fitness_type == 24):
        return [RGAllR, ETB, grey_score*RGAllR]
    elif (fitness_type == 25):
        return [RGAllR, ETB, grey_score*uncorr]

    elif (fitness_type == 26):
        return [RGAllR, ETB, ratio2]
    elif (fitness_type == 27):
        return [RGAllR, ETB, ratio2_sq]
    elif (fitness_type == 28):
        return [RGAllR, ETB, ratio2*ETB]
    elif (fitness_type == 29):
        return [RGGR, ETB, ben_dmg*ETB]

    elif (fitness_type == 30):
        return [RGGR, ETB, RGAllR*grey_score*ETB]
    elif (fitness_type == 31):
        return [RGGR, ETB, ratio2_btm_sq]
    elif (fitness_type == 32):
        return [RGGR, ETB, ben_dmg_sq*RGAllR]    
    elif (fitness_type == 33):
        return [RGGR, ETB, ratio2_btm_sq*ben_dmg_sq]
    elif (fitness_type == 34):
        return [RGGR, ETB, ratio2_btm_sq*ETB]
    else: print("ERROR in pressurize: unknown fitness type.")



def normalize_nodes_by_num_samples(net, num_samples):
    for id in net.nodes():
        #print ("fitness.node_normz(): BEFORE normz = " + str(net[node]['fitness']))
        net.node[id]['fitness'] /= num_samples
        #print ("fitness.node_normz(): AFTER normz = " + str(net[node]['fitness']))


def reset_node_fitness (net):

    for node in net.nodes():
        nx.set_node_attributes(net, 'fitness', {node:0})


