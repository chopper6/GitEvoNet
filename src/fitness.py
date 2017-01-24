#TODO: parse pressurize into here?

import math
from operator import attrgetter

def eval_fitness(population, fitness_type):
    #determines fitness of each individual and orders the population by fitness
    if (fitness_type > 14):
        for p in range(len(population)):
            population[p].fitness = population[p].fitness_parts[2]
        population = sorted(population,key=attrgetter('fitness'), reverse=True)
        return

    if (fitness_type % 3 == 0):
        generic_rank(population)

    else:
        for p in range(len(population)):
            if (fitness_type % 3 == 1):
                population[p].fitness = population[p].fitness_parts[0] * population[p].fitness_parts[1]
            else:
                population[p].fitness = math.pow(population[p].fitness_parts[1],population[p].fitness_parts[0])

    population = sorted(population,key=attrgetter('fitness'), reverse=True)
    #reverse since MAX fitness function


def generic_rank(population):

    for p in range(len(population)):
        population[p].fitness = 0

    for i in range(2): #leaf and hub features
        for p in range(len(population)):
            population[p].id = population[p].fitness_parts[i]
        population.sort(key=attrgetter('id'))
        #no reverse, ie MIN features, to MAX fitness consistent with other definitions
        for p in range(len(population)):
            population[p].fitness += p



def kp_instance_properties(a_result, fitness_type, num_nodes, num_edges):
    #TODO: trim fitness calcs if know which ones to use

    # a_result: the solver returns the following as a list:
    # 0		GENES_in: 		a list, each element in the list is a tuple of three elements: node(gene) ID, its value(benefit), its weight(damage)
    # 1     number_green_genes
    # 2     number_red_genes
    # 3     number_grey genes
    RGGR, ETB, RGAllR, ben_ratio, ben, solver_time = 0,0,0,0,0,0
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
            ben += g[1]
            soln_bens.append(g[1])
            if (g[1] + g[2] != 0):
                ben_ratio += g[1]/(g[1]+g[2])

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

    if (fitness_type == 0):
        return [RGGR, ETB, RGAllR*ETB]
    elif (fitness_type == 1):
        return [RGAllR, ETB, ben_ratio]
    elif (fitness_type == 2):
        return [RGGR, ETB, ben]

    else: print("ERROR in pressurize: unknown fitness type.")



def old_fitness_defs():
    # for reference from prev runs

    '''
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
    '''
    return