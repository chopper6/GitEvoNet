import math, numpy as np, random as rd
import leaf_fitness as l_fitness
import util



def calc_fitness(net, BD_table, configs):
    # also uses log-likelihood normz

    biased = util.boool(configs['biased'])
    bias_on = configs['bias_on']
    leaf_metric = configs['leaf_metric']
    bias_distrib = configs['bias_distribution']
    directed = util.boool(configs['directed'])

    pressure = float(float(configs['pressure'])/float(100))
    pressure_relative = int(len(net.edges())*pressure)


    assert(not biased or not bias_distrib) #not ready to handle local bias on edges

    # fitness_score = 1
    fitness_score = 0

    if not directed: #not biased or not bias_distrib: #ie no local bias

        if not pressure==1:
            all_edges = net.edges()
            rd.shuffle(all_edges)
            pressured_edges = all_edges[:pressure_relative]
            for node in net.nodes():
                effective_node_deg=1
                assert(len(net.edges(node)) == net.in_degree(node) + net.out_degree(node))
                for edge in net.edges(node):
                    if edge in pressured_edges:
                        effective_node_deg +=1
                deg_fitness = BD_table[effective_node_deg]
                if (deg_fitness != 0): fitness_score += deg_fitness


        else:

            #degrees = list(net.degree().values())
            degrees = [net.in_degree(node) + net.out_degree(node) for node in net.nodes()] #making sure...
            degs, freqs = np.unique(degrees, return_counts=True)
            tot = float(sum(freqs))
            #freqs = [(f / tot) * 100 for f in freqs]

            for i in range(len(degs)):
                deg = degs[i]
                deg_fitness = BD_table[deg] #already log-scaled
                # fitness_score *= math.pow(deg_fitness,freqs[i]) #as per node product rule
                if (deg_fitness != 0): fitness_score += freqs[i] * deg_fitness

    else:
        assert(pressure==1) #not ready yet
        node_degs = [[net.in_degree(node), net.out_degree(node)] for node in net.nodes()]
        for node_deg in node_degs:
            in_deg, out_deg = node_deg[0], node_deg[1]
            fitness_score += BD_table[in_deg][out_deg]


    '''
    else: #TODO: fix dis later
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
    '''


    return fitness_score



def build_BD_table(configs, max_deg=100):
    # assumes no conservation score and bernouille pr distribution
    # incld log-normz
    directed = util.boool(configs['directed'])
    leaf_metric = configs['leaf_metric']
    biased = util.boool(configs['biased'])
    global_edge_bias = float(configs['global_edge_bias'])

    if biased:
        global_edge_bias = float(global_edge_bias)
        p = .5 + global_edge_bias
        assert (global_edge_bias > 0 and global_edge_bias < 1)
    else:
        p = .5

    if not directed:
        BD_table = [None for d in range(max_deg)]
        for d in range(max_deg):
            deg_fitness = 0
            for B in range(d+1):
                D = d - B
                prBD = (math.factorial(B + D) / (math.factorial(B) * math.factorial(D))) * math.pow(p, B) * math.pow(1 - p,D)
                assert (prBD >= 0 and prBD <= 1)

                fitBD = l_fitness.node_score(leaf_metric, B, D)
                deg_fitness += prBD * fitBD
            if (deg_fitness != 0): deg_fitness = math.log(deg_fitness, 2) #log likelihood normz
            BD_table[d] = deg_fitness

    else:
        BD_table = [[0 for i in range(max_deg)] for j in range(max_deg)]
        for in_deg in range(max_deg):
            for out_deg in range(max_deg):
                for Bin in range(in_deg + 1):
                    Din = in_deg - Bin
                    prBDin = (math.factorial(Bin + Din) / (math.factorial(Bin) * math.factorial(Din))) * math.pow(p, Bin) * math.pow(1 - p, Din)
                    assert (prBDin >= 0 and prBDin <= 1)
                    for Bout in range(out_deg +1):
                        Dout = out_deg - Bout

                        prBDout = (math.factorial(Bout + Dout) / (math.factorial(Bout) * math.factorial(Dout))) * math.pow(p, Bout) * math.pow(1 - p, Dout)
                        assert (prBDout >= 0 and prBDout <= 1)

                        fitBD = l_fitness.directed_node_score(leaf_metric, Bin, Bout, Din, Dout)
                        BD_table[in_deg][out_deg] += prBDin * prBDout * fitBD #i think...

        for i in range(max_deg):
            for o in range(max_deg):
                if (BD_table[i][o] != 0): BD_table[i][o] = math.log(BD_table[i][o], 2)  # log likelihood normz

    return BD_table