import math, random
from operator import attrgetter

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
    ben_dmg = 0
    uncorr = 0
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

            ben += B
            soln_bens.append(B)
            if (B + D != 0): ben_ratio += B/(B+D)
            if (D > 0): ben_dmg +=  B/D
            else: ben_dmg += B
            
            if (D > 0): uncorr += ((B-D)/D)*B
            else: uncorr += B*B

            # NODE FITNESS inside soln
            print ("Node id = " + str(id))
            if (node_fitness_type == 0):
                net[id]['fitness'] += abs(B-D)
            elif (node_fitness_type == 1):
                net[id]['fitness'] += math.pow(B-D,2)
            elif (node_fitness_type == 2):
                if (B != 0 and D != 0):   net[id]['fitness'] += 1-min(B/D, D/B)
                else: net[id]['fitness'] += 1


        for g in GENES_out:
            B,D=g[1],g[2]
            id = int(g[0])
            if (B + D != 0): ben_ratio += B/(B+D)
            if (D > 0): ben_dmg +=  B/D
            else: ben_dmg += B

            # NODE FITNESS outside soln
            print ("Node id = " + str(id))
            if (node_fitness_type == 0):
                net[id]['fitness'] += abs(B-D)
            elif (node_fitness_type == 1):
                net[id]['fitness'] += math.pow(B-D,2)
            elif (node_fitness_type == 2):
                if (B != 0 and D != 0):   net[id]['fitness'] += 1-min(B/D, D/B)
                else: net[id]['fitness'] += 1

        ETB = sum(set(soln_bens))

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
    else: print("ERROR in pressurize: unknown fitness type.")



def normalize_nodes_by_num_samples(net, num_samples):
    for node in net.nodes():
        print ("fitness.node_normz(): BEFORE normz = " + str(net[node]['fitness']))
        net[node]['fitness'] /= num_samples
        print ("fitness.node_normz(): AFTER normz = " + str(net[node]['fitness']))


def reset_node_fitness (net, node_fitness_type):

    for node in net.nodes():
        net[node]['fitness'] = 0


