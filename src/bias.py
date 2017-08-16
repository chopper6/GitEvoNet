import networkx as nx
from random import SystemRandom as sysRand

def assign_node_consv(population, distrib):
    # since assigns to whole population, will be biased since selection will occur on most fit distribution of conservation scores
    for p in range(len(population)):
        net = population[p].net
        for n in net.nodes():
            assign_a_node_consv(net, n, distrib)

    return population

def assign_a_node_consv(net, node, distrib):
    #redundant with assign_an_edge_consv()

    if (distrib == 'uniform'):
        consv_score = sysRand().uniform(0, 1)
    elif (distrib == 'normal'):
        consv_score = sysRand().normalvariate(.5, .2)
        if consv_score > 1: consv_score = 1
        elif consv_score < 0: consv_score = 0
    elif (distrib == 'bi'):
        consv_score = sysRand().choice([.1, .9])
    elif (distrib == 'half'):
        consv_score = sysRand().choice([.5, 1])

    elif (distrib == 'global_small'):
        consv_score = .75
    elif (distrib == 'global_extreme'):
        consv_score = 1
    elif (distrib == 'global_extreme01'):
        consv_score = sysRand().choice([0, 1])
    else:
        print("ERROR in net_generator(): unknown bias distribution: " + str(distrib))
        return 1

    net.node[node]['conservation_score'] = consv_score


def assign_edge_consv(population, distrib):
    # since assigns to whole population, will be biased since selection will occur on most fit distribution of conservation scores
    for p in range(len(population)):
        net = population[p].net
        for edge in net.edges():
            assign_an_edge_consv(net, edge, distrib)

    return population


def assign_an_edge_consv(net, edge, distrib):
    if (distrib == 'uniform'):
        consv_score = sysRand().uniform(0, 1)
    elif (distrib == 'normal'):
        consv_score = sysRand().normalvariate(.5, .2)
        if consv_score > 1: consv_score = 1
        elif consv_score < 0: consv_score = 0
    elif (distrib == 'bi'):
        consv_score = sysRand().choice([.1, .9])
    elif (distrib == 'half'):
        consv_score = sysRand().choice([.5, 1])

    elif (distrib == 'global_small'):
        consv_score = .75
    elif (distrib == 'global_extreme'):
        consv_score = 1
    elif (distrib == 'global_extreme01'):
        consv_score = sysRand().choice([0, 1])
    else:
        print("ERROR in net_generator(): unknown bias distribution: " + str(distrib))
        return 1

    net[edge[0]][edge[1]]['conservation_score'] = consv_score