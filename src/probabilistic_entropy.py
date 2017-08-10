import math, numpy as np
import leaf_fitness as l_fitness
import util



def calc_fitness(net, BD_table, configs):
    # also uses log-likelihood normz

    biased = util.boool(configs['biased'])
    bias_on = configs['bias_on']
    leaf_metric = configs['leaf_metric']
    bias_distrib = configs['bias_distribution']

    assert(biased and bias_on=='edges' or not biased or not bias_distrib) #not ready to handle local bias on nodes

    # fitness_score = 1
    fitness_score = 0

    if not biased or not edge_distrib: #ie no local bias

        degrees = list(net.degree().values())
        degs, freqs = np.unique(degrees, return_counts=True)
        tot = float(sum(freqs))
        #freqs = [(f / tot) * 100 for f in freqs]

        for i in range(len(degs)):
            deg = degs[i]
            deg_fitness = BD_table[deg] #already log-scaled
            # fitness_score *= math.pow(deg_fitness,freqs[i]) #as per node product rule
            if (deg_fitness != 0): fitness_score += freqs[i] * deg_fitness

    else:
        for n in net.nodes():
            deg = net.in_degree(n) + net.out_degree(n)
            p = net.node[n]['conservation_score']
            node_fitness = 0
            for B in range(deg+1):
                D = deg - B
                prBD = (math.factorial(B + D) / (math.factorial(B) * math.factorial(D))) * math.pow(p, B) * math.pow(1 - p, D)
                assert (prBD >= 0 and prBD <= 1)
                fitBD = l_fitness.node_score(leaf_metric, B, D)
                node_fitness += prBD * fitBD
            if (node_fitness != 0): node_fitness = math.log(node_fitness, 2)  #log likelihood normz

            fitness_score += node_fitness



    return fitness_score



def build_BD_table(leaf_metric, biased, global_edge_bias, max_deg=100):
    # assumes no conservation score and bernouille pr distribution
    # incld log-normz

    if (biased == True):
        global_edge_bias = float(global_edge_bias)
        p = .5 + global_edge_bias
        if (global_edge_bias < 0 or global_edge_bias > 1):
            print("ERROR in pressurize: out of bounds global_edge_bias, p = .5 instead")
            p = .5
    else:
        p = .5

    BD_table = [None for i in range(max_deg)]
    for i in range(max_deg):
        deg_fitness = 0
        for B in range(i+1):
            D = i - B
            prBD = (math.factorial(B + D) / (math.factorial(B) * math.factorial(D))) * math.pow(p, B) * math.pow(1 - p,D)
            assert (prBD >= 0 and prBD <= 1)
            fitBD = l_fitness.node_score(leaf_metric, B, D)
            deg_fitness += prBD * fitBD
        if (deg_fitness != 0): deg_fitness = math.log(deg_fitness, 2) #log likelihood normz
        BD_table[i] = deg_fitness
    return BD_table