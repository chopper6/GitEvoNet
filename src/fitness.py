import math
from operator import attrgetter
import hub_fitness, leaf_fitness

def eval_fitness(population, fitness_direction):
    #determines fitness of each individual and orders the population by fitness
    if (fitness_direction == 'max'): population = sorted(population,key=attrgetter('fitness'), reverse=True)
    elif (fitness_direction == 'min'):  population = sorted(population,key=attrgetter('fitness'))
    else: print("ERROR in fitness.eval_fitness(): unknown fitness_direction " + str(fitness_direction) + ", population not sorted.")

    return population


def node_fitness(net, leaf_metric):
    for n in net.nodes():
        B,D = net.node[n]['benefits'], net.node[n]['damages']
        net.node[n]['fitness'] += leaf_fitness.node_score(leaf_metric, B,D)


def node_scale(net): #TODO: cut i think
    for n in net.nodes():
        info = net.node[n]['fitness']
        num_edges = len(net.in_edges(n) + net.out_edges(n))
        net.node[n]['fitness'] = math.pow(2,info*num_edges)



def node_product(net, scale_node_fitness): #for info version
    fitness_score = 0
    num_0 = 0
    num_under, num_over = 0,0
    for n in net.nodes():
        if net.node[n]['fitness'] == 0:
            num_0 += 1
        else:
            if scale_node_fitness: #hasn't really worked so far
                e2n = len(net.edges(n))
                Inode = net.node[n]['fitness']
                fitness_score += -1*math.log(net.node[n]['fitness'])
            else:
                fitness_score += -1*math.log(net.node[n]['fitness'],2)

    if (num_over != 0 or num_under != 0):
        print("# I < 0 = " + str(num_under) + "\t # I > 1 = " + str(num_over) + "\n")

    if (num_0 > len(net.nodes())/100 and num_0 > 10): print("WARNING: fitness.node_product(): " + str(num_0) + " nodes had 0 fitness out of " + str(len(net.nodes())))
    return fitness_score

#curr blocked in pressurize, TODO: cut it?
def node_entropy(net):
    fitness_score = 0
    for n in net.nodes():
        S = net.node[n]['fitness']
        if S != 0:
            fitness_score += S * math.log(S,2)
    return fitness_score


def node_normz(net, denom):
    if (denom != 0):
        for n in net.nodes():
            net.node[n]['fitness'] /= float(denom)


#use_kp only
def kp_instance_properties(a_result, leaf_metric, leaf_pow, hub_metric, fitness_operator, net, instance_file_name):

    leaf_score = 0
    if (instance_file_name != None): lines = ['' for i in range(5)]

    if len(a_result) > 0:
        # -------------------------------------------------------------------------------------------------
        GENES_in, ALL_GENES, num_green, num_red, num_grey, solver_time = a_result[0], a_result[1], a_result[2], a_result[3], a_result[4], a_result[5]
        # -------------------------------------------------------------------------------------------------

        if (instance_file_name != None): lines[4] += str(solver_time) + ' '
        # -------------------------------------------------------------------------------------------------

        # FITNESS BASED ON KP SOLUTION
        soln_bens = []
        soln_dmgs = []
        all_bens = []
        for g in GENES_in:
            # g[0] gene name, g[1] benefits, g[2] damages, g[3] if in knapsack (binary)
            B,D=g[1],g[2]
            soln_bens.append(B)
            soln_dmgs.append(D)
            all_bens.append(B)

        # -------------------------------------------------------------------------------------------------
        for g in ALL_GENES:
            # g[0] gene name, g[1] benefits, g[2] damages, g[3] if in knapsack (binary)
            B,D=g[1],g[2]
            all_bens.append(B)
            leaf_score += leaf_fitness.node_score(leaf_metric, B, D)

            if (instance_file_name != None):
                indeg = net.in_degree(g[0])
                outdeg = net.out_degree(g[0])
                lines[0] += str(g[0]) + '$' + str(indeg) + '$' + str(outdeg) + ' '
                lines[1] += str(B) + ' '
                lines[2] += str(D) + ' '
                lines[3] += str(g[3]) + ' '
        # -------------------------------------------------------------------------------------------------

        num_genes = len(ALL_GENES)
        leaf_score = math.pow(leaf_score/num_genes,leaf_pow)

        hub_numer = hub_fitness.assign_numer (hub_metric, soln_bens, soln_dmgs)
        hub_denom = hub_fitness.assign_denom (hub_metric, soln_bens, all_bens)
        hub_score = hub_numer/float(hub_denom)

        fitness_score = operate_on_features (leaf_score, hub_score, fitness_operator)



    else:
        print("WARNING in fitness: no results from oracle advice")
        fitness_score, leaf_score, hub_score, node_info = 0,0,0,None

    if (instance_file_name != None):
        with open(instance_file_name, 'a') as file_out:

            for line in lines:
                file_out.write(line + "\n")

    return [fitness_score, leaf_score, hub_score]



def operate_on_features (leaf_score, hub_score, fitness_operator):
    if (fitness_operator=='leaf'): return leaf_score
    elif (fitness_operator=='hub'): return hub_score
    elif (fitness_operator=='add'): return leaf_score+hub_score
    elif (fitness_operator=='multiply'): return leaf_score*hub_score
    elif (fitness_operator=='power'): return math.pow(hub_score,leaf_score)

    elif(fitness_operator == 'unambig'): return leaf_score*hub_score
    else: print("ERROR in fitness.operate_on_features(): unknown fitness operator: " + str(fitness_operator))

