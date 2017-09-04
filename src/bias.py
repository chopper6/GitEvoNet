import networkx as nx
import mutate
from random import SystemRandom as sysRand


def gen_biases(gen_percent, configs):
    assert(configs['bias_on']=='edges')
    distrib = configs['bias_distribution']

    num_mutns = mutate.num_mutations(float(configs['grow_mutation_frequency']), str(configs['mutation_type']), gen_percent)
    num_biases = int(num_mutns * float(configs['edge_to_node_ratio']))

    biases = []
    for i in range(num_biases): biases.append(bias_score(distrib))

    return biases



def assign_node_consv(population, distrib):
    # since assigns to whole population, will be biased since selection will occur on most fit distribution of conservation scores
    for p in range(len(population)):
        net = population[p].net
        for n in net.nodes():
            assign_a_node_consv(net, n, distrib)

    return population

def assign_a_node_consv(net, node, distrib):
    #redundant with assign_an_edge_consv()

    consv_score = bias_score(distrib)
    net.node[node]['conservation_score'] = consv_score


def assign_edge_consv(population, distrib):
    # since assigns to whole population, will be biased since selection will occur on most fit distribution of conservation scores
    for p in range(len(population)):
        net = population[p].net
        for edge in net.edges():
            assign_an_edge_consv(net, edge, distrib)

    return population


def assign_an_edge_consv(net, edge, distrib, bias_given=None):
    if bias_given:
        consv_score = bias_given

    else:
        consv_score = bias_score(distrib)

    net[edge[0]][edge[1]]['conservation_score'] = consv_score


def bias_score(distrib):
    if (distrib == 'uniform'):
        return sysRand().uniform(0, 1)

    elif (distrib == 'normal'):
        consv_score = sysRand().normalvariate(.5, .2)
        if consv_score > 1:
            consv_score = 1
        elif consv_score < 0:
            consv_score = 0
        return consv_score

    elif (distrib == 'bi'):
        return sysRand().choice([.1, .9])

    elif (distrib == 'half'):
        return sysRand().choice([.5, 1])

    elif (distrib == 'global_small'):
        return .75
    elif (distrib == 'global_extreme'):
        return 1
    elif (distrib == 'global_extreme01'):
        return sysRand().choice([0, 1])

    else:
        print("ERROR in net_generator(): unknown bias distribution: " + str(distrib))
        assert(False)
        return 1