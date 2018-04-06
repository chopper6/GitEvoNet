import mutate, pickle, numpy as np
from random import SystemRandom as sysRand


def gen_biases(configs):
    bias_on = configs['bias_on']
    distrib = configs['bias_distribution']

    num_mutns = mutate.num_mutations(float(configs['grow_mutation_frequency']))


    if bias_on == 'edges': num_biases = int(num_mutns * float(configs['edge_to_node_ratio']))
    elif bias_on=='nodes': num_biases = int(num_mutns)
    else: assert(False)

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

def assign_a_node_consv(net, node, distrib, set_bias=None):
    #redundant with assign_an_edge_consv()
    if set_bias: consv_score = set_bias
    else: consv_score = bias_score(distrib)
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



def pickle_bias(net, output_dir, bias_on): #for some reason bias_on isn't recognz'd

        degrees = list(net.degree().values())
        degs, freqs = np.unique(degrees, return_counts=True)
        tot = float(sum(freqs))

        percent = True
        if (percent): freq = [(f/tot)*100 for f in freqs]

        #derive vals from conservation scores
        consv_vals, ngh_consv_vals = [], []
        for deg in degs: #deg consv is normalized by num nodes; node consv is normz by num edges
            avg_consv, ngh_consv, num_nodes = 0,0,0
            for node in net.nodes():
                if (len(net.in_edges(node))+len(net.out_edges(node)) == deg):
                    if (bias_on == 'nodes'):
                        avg_consv += abs(.5-net.node[node]['conservation_score'])

                        avg_ngh_consv = 0
                        for ngh in net.neighbors(node):
                            avg_ngh_consv += net.node[ngh]['conservation_score']

                        num_ngh = len(net.neighbors(node))
                        if num_ngh > 0: avg_ngh_consv /= num_ngh
                        ngh_consv += abs(.5-avg_ngh_consv)

                    elif (bias_on == 'edges'): #node consv is normalized by num edges
                        node_consv, num_edges = 0, 0
                        for edge in net.in_edges(node)+net.out_edges(node):
                            #poss err if out_edges are backwards

                            node_consv += (.5-net[edge[0]][edge[1]]['conservation_score'])
                            num_edges += 1
                        node_consv = abs(node_consv)
                        if (num_edges != 0): node_consv /= num_edges
                        assert(num_edges == deg)
                        avg_consv += node_consv

                    num_nodes += 1

            avg_consv /= num_nodes
            ngh_consv /= num_nodes
            consv_vals.append(avg_consv)
            ngh_consv_vals.append(ngh_consv)
        assert(len(consv_vals) == len(degs))


        with open(output_dir + "/degs_freqs_bias",'wb') as file:
            pickle.dump( [degs, freqs, consv_vals] , file)

