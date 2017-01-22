import math
import reducer, solver
from ctypes import cdll

def pressurize(configs, net):
    # configs:
    pressure = math.ceil((float(configs['PT_pairs_dict'][1][0]) / 100.0))
    tolerance = configs['PT_pairs_dict'][1][1]
    sampling_rounds = int(configs['sampling_rounds'])
    max_sampling_rounds = int(configs['sampling_rounds_max'])
    knapsack_solver = cdll.LoadLibrary(configs['KP_solver_binary'])
    fitness_type = int(configs['fitness_type'])

    leaf_fitness, hub_fitness, solo_fitness = 0,0,0

    num_samples_relative = min(max_sampling_rounds, len(net.nodes()) * sampling_rounds)
    pressure_relative = int(pressure * len(net.nodes()))

    kp_instances = reducer.reverse_reduction(net, pressure_relative, int(tolerance), num_samples_relative, configs['advice_upon'], configs['biased'], configs['BD_criteria'])

    for kp in kp_instances:
        a_result = solver.solve_knapsack(kp, knapsack_solver)

        #various characteristics of a result
        inst_leaf_fitness, inst_hub_fitness, instance_time  = kp_instance_properties(a_result, fitness_type, len(net.nodes()), len(net.edges()))

        leaf_fitness += inst_leaf_fitness
        hub_fitness += inst_hub_fitness
        solo_fitness += instance_time

    leaf_fitness /= num_samples_relative
    hub_fitness /= num_samples_relative
    solo_fitness /= num_samples_relative

    return [leaf_fitness, hub_fitness, solo_fitness]



def kp_instance_properties(a_result, fitness_type, num_nodes, num_edges):
    #TODO: trim fitness calcs if know which ones to use

    # a_result: the solver returns the following as a list:
    # 0		GENES_in: 		a list, each element in the list is a tuple of three elements: node(gene) ID, its value(benefit), its weight(damage)
    # 1     number_green_genes
    # 2     number_red_genes
    # 3     number_grey genes
    RGGR, ETB, dist_in_sack, dist_sq_in_sack, ETB_ratio, RGAllR, ben_ratio, ratiodist, solver_time = 0,0,0,0,0,0,0,0,0
    soln_size = 1
    if len(a_result) > 0:
        # -------------------------------------------------------------------------------------------------
        GENES_in, num_green, num_red, num_grey, solver_time = a_result[0], a_result[1], a_result[2], a_result[3], a_result[4]
        # -------------------------------------------------------------------------------------------------
        soln_bens = []
        soln_size = len(GENES_in)
        for g in GENES_in:
            # g[0] gene name, g[1] benefits, g[2] damages, g[3] if in knapsack (binary)
            # hub score eval pt1
            dist_in_sack += (g[1] - g[2])
            dist_sq_in_sack += math.pow((g[1] - g[2]), 2)
            soln_bens.append(g[1])
            if (g[1] + g[2] != 0): 
                ben_ratio += g[1]/(g[1]+g[2])
                ratiodist += dist_in_sack*ben_ratio
            else: ratiodist += dist_in_sack

        # hub score eval pt2
        ETB = sum(set(soln_bens))
        if (sum(soln_bens) != 0):
            ETB_ratio = sum(set(soln_bens)) / sum(soln_bens)
        else:
            ETB_ratio = sum(set(soln_bens))

        # leaf score eval
        if (num_grey != 0):
            RGGR = (num_green + num_red) / num_grey
        else:
            RGGR = (num_green + num_red)
        RGAllR = (num_green + num_red) / (num_green + num_red + num_grey)

    else:
        print("WARNING in pressurize: no results from oracle advice")

    if (fitness_type == 0 or fitness_type == 1 or fitness_type == 2):
        return [RGGR, ETB, ben_ratio]
    elif (fitness_type == 3 or fitness_type == 4 or fitness_type == 5):
        return [RGAllR, ETB, ben_ratio]
    elif (fitness_type == 6 or fitness_type == 7 or fitness_type == 8):
        return [RGGR, dist_in_sack, ben_ratio]
    elif (fitness_type == 9 or fitness_type == 10 or fitness_type == 11):
        return [RGAllR, dist_in_sack, ben_ratio]
    elif (fitness_type == 12 or fitness_type == 13 or fitness_type == 14): #doesn't work at all
        node_to_edge_ratio = num_nodes/ num_edges
        return [node_to_edge_ratio, dist_in_sack, ben_ratio]
    elif (fitness_type == 15):
        return [RGAllR, ETB, ben_ratio]
    elif (fitness_type == 16):
        return [RGAllR, ETB, dist_in_sack]
    elif (fitness_type == 17):
        return [RGAllR, ETB, RGAllR*ETB]
    elif (fitness_type == 18):
        return [RGAllR, ETB, math.pow(ETB,RGAllR)]
    elif (fitness_type == 19):
        return [RGAllR, ETB, ben_ratio*ETB]
    elif (fitness_type == 20):
        return [RGAllR, ETB, ratiodist]
    elif (fitness_type == 21):
        return [RGAllR, ETB, ben_ratio/soln_size]
    elif (fitness_type == 22):
        return [RGAllR, ETB, ben_ratio*RGAllR]
    else: print("ERROR in pressurize: unknown fitness type.")
