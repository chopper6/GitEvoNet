import math
import random as rd
#from random import SystemRandom as rd

def mutate(configs, net, worker_ID):
    print("worker " + str(worker_ID) + " start with " + str(rd.random()))
    #rd.seed(randSeed)
    # mutation operations: rm edge, add edge, rewire an edge, change edge sign, reverse edge direction

    #how to elegantly pass booleans
    # note: bias and boundary are not curr implemented
    bias = configs['use_mutation_bias']
    boundary = configs['constrain_node:edge_ratio']
    scale = configs['scale_mutation_frequency_by_net_size']
    stoch_mutn = configs['stochastic_mutation']

    add_freq = float(configs['add_edge_mutation_frequency'])
    rm_freq = float(configs['remove_edge_mutation_frequency'])
    rewire_freq = float(configs['rewire_mutation_frequency'])
    sign_freq = float(configs['sign_mutation_frequency'])
    reverse_freq = float(configs['reverse_edge_mutation_frequency'])
    grow_freq = float(configs['grow_mutation_frequency'])
    shrink_freq = float(configs['shrink_mutation_frequency'])
    #TODO: remove set stoch, ect
    stoch_mutn = True
    scale = False 
    '''
    # BOUNDARY CURR NOT IMPLEMENTED
    num_nodes = len(net.nodes())
    num_edges = len(net.edges())
    if (boundary == False):
        rm_allowed = True
        add_allowed = True
    else:
        if (num_nodes == num_edges): rm_allowed = False
        else: rm_allowed = True
        if (2*num_nodes == num_edges): add_allowed = False
        else: add_allowed = True
    '''

    #BIAS CURR NOT IMPLEMENTED, old code:
    '''
    if (bias == True):
        ngh_deg = nx.average_neighbor_degree(net, nodes=[node])
        ngh_deg = ngh_deg[node]
        if (ngh_deg != 0):
            add_prob = (net.degree(node)) / (ngh_deg + net.degree(node))
        else:
            add_prob = .5
    else:
        add_prob = .5
    '''


    # --------- MUTATIONS ------------- #

    #GROW (ADD NODE)
    #starts unconnected
    num_grow = num_mutations(grow_freq, net, stoch_mutn, scale)
    before = len(net.nodes())
    for i in range(num_grow):
        node = len(net.nodes())
        net.add_node(node)
        #print(before, len(net.nodes()))
    
    #SHRINK (REMOVE NODE)
    num_shrink = num_mutations(shrink_freq, net, stoch_mutn, scale)
    for i in range(num_shrink):
        node = rd.sample(net.nodes(), 1)
        node = node[0]
        net.remove_node(node)

    #ADD EDGE
    num_add = num_mutations(add_freq, net, stoch_mutn, scale)
    for i in range(num_add):
        pre_size = post_size = len(net.nodes())
        while (pre_size == post_size):  # ensure that net adds
            node = node2 = rd.sample(net.nodes(), 1)
            node = node[0]
            node2 = node
            while (node2 == node):
                node2 = rd.sample(net.nodes(), 1)
                node2 = node2[0]
            sign = rd.randint(0, 1)
            if (sign == 0):     sign = -1
            net.add_edge(node, node2, sign=sign)
            #post_size = len(net.nodes())
            post_size = pre_size +1 #TODO remove this, added due to very long wait in loops

    #REMOVE EDGE
    num_rm = num_mutations(rm_freq, net, stoch_mutn, scale)
    for i in range(num_rm):
        edge = rd.sample(net.edges(), 1)
        edge = edge[0]
        net.remove_edge(edge[0], edge[1])

    #REWIRE EDGE
    num_rewire = num_mutations(rewire_freq, net, stoch_mutn, scale)
    for i in range(num_rewire):
        pre_edges = post_edges = len(net.edges())
        post_edges = pre_edges+1
        while (pre_edges != post_edges):    #ensure sucessful rewire
            edge = rd.sample(net.edges(), 1)
            edge = edge[0]
            sign = net[edge[0]][edge[1]]['sign']
            net.remove_edge(edge[0], edge[1])
            node = edge[0]
            node2 = node
            while (node2 == node):
                node2 = rd.sample(net.nodes(), 1)
                node2 = node2[0]
            net.add_edge(node, node2, sign=sign)

            post_edges = len(net.edges())
            if (post_edges != pre_edges):
                net.add_edge(edge[0], edge[1], sign=sign)  #rewire failed, undo rm'd edge

    #REVERSE EDGE DIRECTION
    num_reverse = num_mutations(reverse_freq, net, stoch_mutn, scale)
    for i in range(num_reverse):
        pre_edges = post_edges = len(net.edges())
        post_edges = pre_edges + 1
        while (pre_edges != post_edges):
            pre_edges = post_edges = len(net.edges())
            edge = rd.sample(net.out_edges(), 1)
            edge = edge[0]
            sign = net[edge[0]][edge[1]]['sign']
            net.remove_edge(edge[0], edge[1])
            net.add_edge(edge[1], edge[0], sign=sign)

            post_edges = len(net.edges())
            if (pre_edges != post_edges):
                net.add_edge(edge[0], edge[1], sign=sign) #reverse failed, undo rm'd edge

    #CHANGE EDGE SIGN
    num_sign = num_mutations(sign_freq, net, stoch_mutn, scale)
    for i in range(num_sign):
        pre_edges = len(net.edges())
        edge = rd.sample(net.out_edges(), 1)
        edge = edge[0]
        net[edge[0]][edge[1]]['sign'] = -1 * net[edge[0]][edge[1]]['sign']
        post_edges = len(net.edges())
        if (pre_edges != post_edges):   print("ERROR: mutn sign change has changed the number of edges!")


def num_mutations(mutn_freq, net, stoch, scale):
    if (stoch == True):     mutn_freq = (rd.uniform(0,20)*mutn_freq)

    if (scale == True): mutn_freq*= len(net.nodes())

    num_mutn = round(mutn_freq)
 
    return num_mutn

