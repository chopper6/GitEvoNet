import math
import random as rd
import networkx as nx
# from random import SystemRandom as rd

def mutate(configs, net):
    # mutation operations: rm edge, add edge, rewire an edge, change edge sign, reverse edge direction

    add_freq = float(configs['add_edge_mutation_frequency'])
    rm_freq = float(configs['remove_edge_mutation_frequency'])
    rewire_freq = float(configs['rewire_mutation_frequency'])
    sign_freq = float(configs['sign_mutation_frequency'])
    reverse_freq = float(configs['reverse_edge_mutation_frequency'])
    grow_freq = float(configs['grow_mutation_frequency'])
    shrink_freq = float(configs['shrink_mutation_frequency'])

    # --------- MUTATIONS ------------- #

    # GROW (ADD NODE)
    # starts unconnected
    num_grow = num_mutations(grow_freq)
    for i in range(num_grow):
        pre_size = post_size = len(net.nodes())
        while (pre_size == post_size):
            node_num = rd.randint(0, len(net.nodes()) * 10)  # hope to hit number that doesn't already exist
            net.add_node(node_num)
            post_size = len(net.nodes())

    # SHRINK (REMOVE NODE)
    num_shrink = num_mutations(shrink_freq)
    pre_size = len(net.nodes())
    for i in range(num_shrink):
        node = rd.sample(net.nodes(), 1)
        node = node[0]
        net.remove_node(node)
        post_size = len(net.nodes())
        if (pre_size == post_size): print("MUTATE SHRINK() ERR: node not removed.")

    # ADD EDGE
    num_add = num_mutations(add_freq)
    for i in range(num_add):
        pre_size = post_size = len(net.edges())
        while (pre_size == post_size):  # ensure that net adds
            node = rd.sample(net.nodes(), 1)
            node = node[0]
            count = 0
            while (pre_size == post_size and count < 100000):
                count += 1
                node2 = node
                while (node2 == node):
                    node2 = rd.sample(net.nodes(), 1)
                    node2 = node2[0]

                sign = rd.randint(0, 1)
                if (sign == 0):     sign = -1
                net.add_edge(node, node2, sign=sign)
                post_size = len(net.edges())

    # REMOVE EDGE
    num_rm = num_mutations(rm_freq)
    for i in range(num_rm):
        pre_size = post_size = len(net.edges())
        count = 0
        while (pre_size == post_size):
            count += 1
            node = rd.sample(net.nodes(),1)  #mutation by node
            node = node[0]
            edges = net.out_edges(node)
            if (len(edges) > 0):
                edge = rd.sample(net.edges(node), 1)
                edge = edge[0]

                net.remove_edge(edge[0], edge[1])
                post_size = len(net.edges())
                if (post_size==pre_size): print("WARNING: mutate remove edge failed, trying again.")

    # REWIRE EDGE
    num_rewire = num_mutations(rewire_freq)
    for i in range(num_rewire):
        pre_edges = len(net.edges())
        rewire_success = False
        while (rewire_success==False):  # ensure sucessful rewire
            node = rd.sample(net.nodes(),1)  #by node
            node = node[0]
            edges = net.out_edges(node)+net.in_edges(node)
            if (len(edges) > 0):
                edge = rd.sample(edges, 1)
                edge = edge[0]
                sign = net[edge[0]][edge[1]]['sign']

                count = 0
                node_success = False
                while (node_success==False and count < 10000): #try repeatedly from same starting node
                    count += 1
                    node2 = node
                    while (node2 == node):
                        node2 = rd.sample(net.nodes(), 1)
                        node2 = node2[0]

                    if (rd.random() < .5): net.add_edge(node, node2, sign=sign) #possible reverse
                    else: net.add_edge(node2, node, sign=sign)
                    post_edges = len(net.edges())
                    if (post_edges > pre_edges): #check that edge successfully added
                        net.remove_edge(edge[0], edge[1])
                        post_edges = len(net.edges())
                        if (post_edges==pre_edges): #check that edge successfully removed
                            node_success = True
                            rewire_success = True
                        else:
                            print("ERROR IN REWIRE: num edges not kept constant")
                            return

    # REVERSE EDGE DIRECTION
    num_reverse = num_mutations(reverse_freq)
    for i in range(num_reverse):
        pre_edges = post_edges = len(net.edges())
        post_edges = pre_edges + 1
        while (pre_edges != post_edges):
            node = rd.sample(net.nodes(),1)  #by node
            node = node[0]
            edges = net.out_edges(node)
            count = 0
            if (len(edges) > 0):
                post_edges = pre_edges + 1
                while (post_edges != pre_edges and count<10): #each node has 10 tries
                    count += 1
                    edge = rd.sample(edges, 1)
                    edge = edge[0]
                    sign = net[edge[0]][edge[1]]['sign']
                    net.remove_edge(edge[0], edge[1])
                    net.add_edge(edge[1], edge[0], sign=sign)

                    post_edges = len(net.edges())
                    if (pre_edges != post_edges):
                        net.add_edge(edge[0], edge[1], sign=sign)  # reverse failed, undo rm'd edge

    # CHANGE EDGE SIGN
    num_sign = num_mutations(sign_freq)
    for i in range(num_sign):
        pre_edges = len(net.edges())
        post_edges = pre_edges + 1
        while (pre_edges != post_edges):
            node = rd.sample(net.nodes(), 1)  # mutation by node
            node = node[0]
            edges = net.out_edges(node)
            if (len(edges) > 0):
                edge = rd.sample(net.edges(node), 1)
                edge = edge[0]

                net[edge[0]][edge[1]]['sign'] = -1 * net[edge[0]][edge[1]]['sign']
                post_edges = len(net.edges())


def num_mutations(mutn_freq):
    # note: mutation should be < 1 OR, if > 1, an INT
    if (mutn_freq < 1):
        if (rd.random() < mutn_freq):
            return 1
        else:
            return 0

    else:
        return rd.randint(0, mutn_freq)

