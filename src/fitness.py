import math, random
from operator import attrgetter
import networkx as nx
import hub_fitness, leaf_fitness

def eval_fitness(population, fitness_direction):
    #determines fitness of each individual and orders the population by fitness
    for p in range(len(population)):
        population[p].fitness = population[p].fitness_parts[2]

    if (fitness_direction == 'max'): population = sorted(population,key=attrgetter('fitness'), reverse=True)
    elif (fitness_direction == 'min'):  population = sorted(population,key=attrgetter('fitness'))
    else: print("ERROR in fitness.eval_fitness(): unknown fitness_direction " + str(fitness_direction) + ", population not sorted.")

    return population


def node_fitness(net, leaf_metric):
    for n in net.nodes():
        B,D = net.node[n]['benefits'], net.node[n]['damages']
        if (B+D == 0): print ("WARNING fitness.node_fitness(): B+D == 0")
        net.node[n]['fitness'] += leaf_fitness.node_score(leaf_metric, B,D)
        #print(net[node]['fitness'])

def node_product(net):
    fitness_score = 1
    num_0 = 0
    for n in net.nodes():
        if net.node[n]['fitness'] == 0: 
            #print("\nWARNING: in fitness.node_product(), node fitness = 0, discounted.\n\n")
            num_0 += 1
        else: fitness_score *= net.node[n]['fitness']
    if (num_0 > 0): print("WARNING: fitness.node_product(): " + str(num_0) + " nodes had 0 fitness out of " + str(len(net.nodes())))
    return fitness_score

def node_normz(net, denom):
    if (denom != 0):
        for n in net.nodes():
            net.node[n]['fitness'] /= denom

#use_kp only
def kp_instance_properties(a_result, leaf_metric, leaf_operator, leaf_pow, hub_metric, hub_operator, fitness_operator, net, instance_file_name):

    #LEAF MEASURES
    RGAR, leaf_control = 0,0
    if (leaf_operator == 'average' or leaf_operator == 'sum' or leaf_operator == 'inv sum'): leaf_score = 0
    elif (leaf_operator == 'product'): leaf_score = 1
    else: print ("ERROR in fitness(): unknown leaf_operator: " + str(leaf_operator))

    #HUB MEASURES
    ETB, effic, effic2 = 0,0,0
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
        soln_dmgs = []

        for g in GENES_in:
            # g[0] gene name, g[1] benefits, g[2] damages, g[3] if in knapsack (binary)
            B,D=g[1],g[2]
            soln_bens.append(B)
            soln_bens_sq.append(math.pow(B,2))
            soln_dmgs.append(D)

        # -------------------------------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------------------
        # FITNESS BASED ON ALL GENES
        all_ben = []
        all_dmg = []
        for g in ALL_GENES:
            # g[0] gene name, g[1] benefits, g[2] damages, g[3] if in knapsack (binary)
            B,D=g[1],g[2]
            if (leaf_operator == 'average' or leaf_operator == 'sum' or leaf_operator == 'inv sum'): leaf_score += leaf_fitness.node_score(leaf_metric, B, D)
            elif (leaf_operator == 'product'): leaf_score *= leaf_fitness.node_score(leaf_metric, B, D)
            else: print("ERROR in fitness(): unknown leaf_operator: " + str(leaf_operator))
            RGAR += leaf_fitness.node_score("RGAR", B, D)

            all_ben.append(B)
            all_dmg.append(D)

            if (instance_file_name != None):
                indeg = net.in_degree(g[0])
                outdeg = net.out_degree(g[0])
                lines[0] += str(g[0]) + '$' + str(indeg) + '$' + str(outdeg) + ' '
                lines[1] += str(B) + ' '
                lines[2] += str(D) + ' '
                lines[3] += str(g[3]) + ' '

        num_genes = len(ALL_GENES)

        # -------------------------------------------------------------------------------------------------
        leaf_denom = leaf_fitness.assign_denom (leaf_metric, num_genes)
        if (leaf_operator == 'average'):
            leaf_score /= leaf_denom #ASSUMES ALL LEAF METRICS ARE CALC'D PER EACH NODE
            leaf_score = math.pow(leaf_score,leaf_pow)

        elif (leaf_operator == 'sum'): leaf_score = math.pow(leaf_score/leaf_denom,leaf_pow)
        elif (leaf_operator == 'inv sum'): leaf_score = 1/leaf_score
        elif (leaf_operator == 'product'): leaf_score = math.pow(leaf_score, leaf_pow/leaf_denom)
        RGAR /= leaf_fitness.assign_denom ("RGAR", num_genes)

        hub_score = hub_fitness.assign_numer (hub_metric, soln_bens, soln_dmgs, soln_bens_sq)
        hub_denom = hub_fitness.assign_denom (hub_metric, soln_bens)
        hub_score /= float(hub_denom)
        if (hub_operator == 'pow'): hub_score = math.pow(hub_score, 1/len(GENES_in))
        elif (hub_operator == 'mult'): hub_score /= len(GENES_in)
        elif (hub_operator == 'sum all'):
            if (sum(all_ben)>0): hub_score /= float(sum(all_ben))
        elif (hub_operator == 'inv sum'): hub_score = 1/hub_score
        elif (hub_operator == 'inv leaf'): hub_score = leaf_score/hub_score
        elif (hub_operator == 'leaf'): hub_score /= leaf_score

        fitness_score = operate_on_features (leaf_score, hub_score, fitness_operator)



    else:
        print("WARNING in pressurize: no results from oracle advice")
        fitness_score, leaf_score, hub_score, node_info = 0,0,0,None

    if (instance_file_name != None):
        with open(instance_file_name, 'a') as file_out:
            for line in lines:
                file_out.write(line + "\n")

    return [leaf_score, hub_score, fitness_score]



def operate_on_features (leaf_score, hub_score, fitness_operator):
    if (fitness_operator=='leaf'): return leaf_score
    elif (fitness_operator=='hub'): return hub_score
    elif (fitness_operator=='add'): return leaf_score+hub_score
    elif (fitness_operator=='multiply'): return leaf_score*hub_score
    elif (fitness_operator=='power'): return math.pow(hub_score,leaf_score)

    elif(fitness_operator == 'unambig'): return leaf_score*hub_score
    else: print("ERROR in fitness.operate_on_features(): unknown fitness operator: " + str(fitness_operator))

