import math, random
from operator import attrgetter
import networkx as nx
import hub_fitness, leaf_fitness, node_fitness

def eval_fitness(population):
    #determines fitness of each individual and orders the population by fitness
    for p in range(len(population)):
        population[p].fitness = population[p].fitness_parts[2]
    population = sorted(population,key=attrgetter('fitness'), reverse=True)
    #reverse since MAX fitness function
    return population


def kp_instance_properties(a_result, leaf_metric, hub_metric, fitness_operator, net, track_node_fitness, node_info, instance_file_name):

    #LEAF MEASURES
    RGAR, RGMG, ratio, ratio_onesided, ratio_sq, ratio_btm_sq, leaf_control, dual1 = 0,0,0,0,0,0,0,0
    max_sum, max_sum_sq, combo_sum, combo_sum_sq = 0,0,0,0
    leaf_score = 0
    if (track_node_fitness == True): Bmax = len(node_info['freq'])-1

    #HUB MEASURES
    ETB, dist, dist_sq, effic, effic2, effic4 = 0,0,0,0,0,0
    if (instance_file_name != None): lines = ['' for i in range(5)]

    if len(a_result) > 0:
        # -------------------------------------------------------------------------------------------------
        GENES_in, ALL_GENES, num_green, num_red, num_grey, solver_time = a_result[0], a_result[1], a_result[2], a_result[3], a_result[4], a_result[5]
        # -------------------------------------------------------------------------------------------------

        if (instance_file_name != None): lines[4] += str(solver_time) + ' '
        # -------------------------------------------------------------------------------------------------
        # FITNESS BASED ON KP SOLUTION
        soln_bens = []
        soln_bens_sq = []
        soln_bens_4 = []

        for g in GENES_in:
            # g[0] gene name, g[1] benefits, g[2] damages, g[3] if in knapsack (binary)
            B,D=g[1],g[2]
            soln_bens.append(B)
            soln_bens_sq.append(math.pow(B,2))
            soln_bens_4.append(math.pow(B,4))

            if (track_node_fitness == True): 
                if (B > Bmax or D > Bmax):
                    xadfdas=3 
                    #print("WARNING fitness(): B = " + str(B) + ", D = " + str(D) + " not included in node_info.")
                else: node_info['freq in solution'][B][D] += 1
        if (track_node_fitness == True): node_info = node_fitness.normz(node_info, len(GENES_in), 'freq in solution')
        # -------------------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------------------
        # FITNESS BASED ON ALL GENES
        all_ben = []
        all_dmg = []
        for g in ALL_GENES:
            # g[0] gene name, g[1] benefits, g[2] damages, g[3] if in knapsack (binary)
            B,D=g[1],g[2]
            leaf_score += leaf_fitness.node_score(leaf_metric, B, D)
            RGAR += leaf_fitness.node_score("RGAR", B, D)

            all_ben.append(B)
            all_dmg.append(D)

            dist +=  abs(B-D)
            dist_sq += math.pow(B-D,2)
            combo_sum += B+D
            combo_sum_sq += math.pow(B+D, 2)

            if (instance_file_name != None):
                indeg = net.in_degree(g[0])
                outdeg = net.out_degree(g[0])
                lines[0] += str(g[0]) + '$' + str(indeg) + '$' + str(outdeg) + ' '
                lines[1] += str(B) + ' '
                lines[2] += str(D) + ' '
                lines[3] += str(g[3]) + ' '


            if (track_node_fitness==True):
                if (B > Bmax or D > Bmax): 
                    xadsf=3
                    #print("WARNING fitness(): B = " + str(B) + ", D = " + str(D) + " not included in node_info.")
                else: node_info['freq'][B][D] += 1
        if (track_node_fitness == True): node_info = node_fitness.normz(node_info, len(ALL_GENES), 'freq')

        num_genes = len(ALL_GENES)

        # -------------------------------------------------------------------------------------------------

        leaf_denom = leaf_fitness.assign_denom (leaf_metric, num_genes)
        leaf_score /= leaf_denom #ASSUMES ALL LEAF METRICS ARE CALC'D PER EACH NODE
        RGAR /= leaf_fitness.assign_denom ("RGAR", num_genes)

        hub_score = hub_fitness.assign_numer (hub_metric, soln_bens, soln_bens_sq, soln_bens_4)
        hub_denom = hub_fitness.assign_denom (hub_metric, soln_bens)
        hub_score /= hub_denom
        ETB = hub_fitness.assign_numer ("ETB", soln_bens, soln_bens_sq, soln_bens_4)
        ETB /= hub_fitness.assign_denom ("ETB", soln_bens)

        fitness_score = operate_on_features (leaf_score, hub_score, fitness_operator)


        if (track_node_fitness==True):
            node_info = node_fitness.calc(node_info, leaf_metric, hub_metric, fitness_operator, soln_bens, num_genes)


    else:
        print("WARNING in pressurize: no results from oracle advice")
        fitness_score = 0

    if (instance_file_name != None):
        with open(instance_file_name, 'a') as file_out:
            for line in lines:
                file_out.write(line + "\n")
    return [RGAR, ETB, fitness_score, node_info]



def operate_on_features (leaf_score, hub_score, fitness_operator):
    if (fitness_operator=='leaf'): return leaf_score
    elif (fitness_operator=='hub'): return hub_score
    elif (fitness_operator=='add'): return leaf_score+hub_score
    elif (fitness_operator=='multiply'): return leaf_score*hub_score
    elif (fitness_operator=='power'): return math.pow(hub_score,leaf_score)
    else: print("ERROR in fitness.operate_on_features(): unknown fitness operator.")

