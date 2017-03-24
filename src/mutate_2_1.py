import math
import random as rd
import networkx as nx
# from random import SystemRandom as rd

def mutate(configs, net, gen_percent):
    # mutation operations: rm edge, add edge, rewire an edge, change edge sign, reverse edge direction

    rewire_freq = float(configs['rewire_mutation_frequency'])
    sign_freq = float(configs['sign_mutation_frequency'])
    grow_freq = float(configs['grow_mutation_frequency'])
    shrink_freq = float(configs['shrink_mutation_frequency'])

    mutn_type = str(configs['mutation_type'])
    # --------- MUTATIONS ------------- #
    # GROW (ADD NODE + 2 edges)
    # starts unconnected
    num_grow = num_mutations(grow_freq, mutn_type, gen_percent)
    for i in range(num_grow):

        #ADD NODE
        pre_size = post_size = len(net.nodes())
        while (pre_size == post_size):
            node_num = rd.randint(0, len(net.nodes()) * 10)  # hope to hit number that doesn't already exist
            net.add_node(node_num)
            post_size = len(net.nodes())

        #ADD 2 EDGES
        for i in range(2):
            pre_size = post_size = len(net.edges())
            while (pre_size == post_size):  # ensure that net adds
                node = rd.sample(net.nodes(), 1)
                node = node2 = node[0]
                while (node2 == node):
                    node2 = rd.sample(net.nodes(), 1)
                    node2 = node2[0]

                sign = rd.randint(0, 1)
                if (sign == 0):     sign = -1
                net.add_edge(node, node2, sign=sign)
                post_size = len(net.edges())


    # SHRINK (REMOVE NODE + 2 EDGES)
    num_shrink = num_mutations(shrink_freq, mutn_type, gen_percent)
    pre_size = len(net.nodes())
    for i in range(num_shrink):

        #REMOVE NODE
        node = rd.sample(net.nodes(), 1)
        node = node[0]
        net.remove_node(node)
        post_size = len(net.nodes())
        if (pre_size == post_size): print("MUTATE SHRINK() ERR: node not removed.")

        # REMOVE 2 EDGES
        for i in range(2):
            pre_size = post_size = len(net.edges())
            while (pre_size == post_size):
                edge = rd.sample(net.edges(),1)
                edge = edge[0]
                net.remove_edge(edge[0], edge[1])
                if (post_size == pre_size): print("WARNING: mutate remove edge failed, trying again.")


    # REWIRE EDGE
    num_rewire = num_mutations(rewire_freq, mutn_type, gen_percent)
    for i in range(num_rewire):
        pre_edges = len(net.edges())
        rewire_success = False
        while (rewire_success==False):  # ensure sucessful rewire
            edge = rd.sample(net.edges(), 1)
            edge = edge[0]
            #sign = net[edge[0]][edge[1]]['sign']

            node = rd.sample(net.nodes(), 1)
            node = node[0]
            node2 = node
            while (node2 == node):
                node2 = rd.sample(net.nodes(), 1)
                node2 = node2[0]
            sign = rd.randint(0, 1)
            if (sign == 0):     sign = -1

            if (rd.random() < .5): net.add_edge(node, node2, sign=sign)
            else: net.add_edge(node2, node, sign=sign)
            post_edges = len(net.edges())
            if (post_edges > pre_edges): #check that edge successfully added
                net.remove_edge(edge[0], edge[1])
                post_edges = len(net.edges())
                if (post_edges==pre_edges): #check that edge successfully removed
                    rewire_success = True
                else:
                    print("ERROR IN REWIRE: num edges not kept constant")
                    return


    # CHANGE EDGE SIGN
    num_sign = num_mutations(sign_freq, mutn_type, gen_percent)
    for i in range(num_sign):
        pre_edges = len(net.edges())
        post_edges = pre_edges + 1
        while (pre_edges != post_edges):
            edge = rd.sample(net.edges(), 1)
            edge = edge[0]
            net[edge[0]][edge[1]]['sign'] = -1 * net[edge[0]][edge[1]]['sign']
            post_edges = len(net.edges())
            if (post_edges != pre_edges): print("ERROR IN SIGN CHANGE: num edges not kept constant.")


def num_mutations(base_mutn_freq, mutn_type, gen_percent):
    # note: mutation should be < 1 OR, if > 1, an INT
    mutn_freq=0

    if (mutn_type == 'static' or base_mutn_freq == 0):  mutn_freq = base_mutn_freq
    elif (mutn_type == 'dynamic'):
        mutn_freq = math.ceil(base_mutn_freq - base_mutn_freq*gen_percent)
        if (mutn_freq<=0): print("WARNING in mutate.num_mutations(): dynamic mutation yield 0 freq.")
    else: print("ERROR in mutation(): unknown mutation type.")

    if (mutn_freq == 0): return 0
    elif (mutn_freq < 1):
        if (rd.random() < mutn_freq):
            return 1
        else:
            return 0

    else:
        return rd.randint(0, mutn_freq)

