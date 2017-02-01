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

    pref_type = int(configs['preferential_type'])
    node_fitness_type = int(configs['node_fitness_type'])

    # --------- MUTATIONS ------------- #

    # GROW (ADD NODE)
    # starts unconnected
    num_grow = num_mutations(grow_freq)
    for i in range(num_grow):
        pre_size = post_size = len(net.nodes())
        while (pre_size == post_size):
            node_num = rd.randint(0, len(net.nodes()) * 100000)  # hope to hit number that doesn't already exist
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


    # PREFERENTIALLY ADD EDGE
    num_add = num_mutations(add_freq)
    for i in range(num_add):
        pre_size = post_size = len(net.edges())
        count = 0
        while (pre_size == post_size and count < 10000):  # ensure that net adds
            count += 1
            node = rd.sample(net.nodes(), 1)
            node = node[0]
            node2 = node
            while (node2 == node):
                node2 = rd.sample(net.nodes(), 1)
                node2 = node2[0]

            pref_score = calc_tractability(net, node, node2, pref_type, node_fitness_type)

            if (rd.random() < pref_score):
                sign = rd.randint(0, 1)
                if (sign == 0):     sign = -1
                net.add_edge(node, node2, sign=sign)
                post_size = len(net.edges())

    # REMOVE EDGE
    num_rm = num_mutations(rm_freq)
    for i in range(num_rm):
        pre_size = post_size = len(net.edges())
        count = 0
        while(pre_size == post_size and count < 10000):
            count += 1
            edge = rd.sample(net.edges(), 1)
            edge = edge[0]

            pref_score = calc_tractability(net, edge[0], edge[1], pref_type, node_fitness_type)

            if (rd.random() < 1-pref_score):
                    net.remove_edge(edge[0], edge[1])
                    post_size = len(net.edges())

    # REWIRE EDGE
    num_rewire = num_mutations(rewire_freq)
    for i in range(num_rewire):
        pre_edges = post_edges = len(net.edges())
        post_edges = pre_edges + 1
        count = 0
        while (pre_edges != post_edges and count < 10000):  # ensure sucessful rewire
            count += 1
            edge = rd.sample(net.edges(), 1)
            edge = edge[0]
            sign = net[edge[0]][edge[1]]['sign']
            rm_pref_score = calc_tractability(net,edge[0],edge[1],pref_type, node_fitness_type)

            if (rd.random() < rm_pref_score):
                if (rd.random() < .5): node = edge[0]
                else: node = edge[1]
                node2 = node
                while (node2 == node):
                    node2 = rd.sample(net.nodes(), 1)
                    node2 = node2[0]

                add_pref_score = calc_tractability(net,node,node2,pref_type, node_fitness_type)

                if (rd.random < add_pref_score):
                    net.remove_edge(edge[0], edge[1])

                    if (rd.random() < .5): net.add_edge(node, node2, sign=sign)
                    else: net.add_edge(node2, node, sign=sign)

                    post_edges = len(net.edges())
                    if (post_edges != pre_edges):
                        net.add_edge(edge[0], edge[1], sign=sign)  # rewire failed, undo rm'd edge
                        post_edges = len(net.edges())
                        if (post_edges != pre_edges): print("MUTATION ERR: undo rm edge failed.")

    # REVERSE EDGE DIRECTION
    num_reverse = num_mutations(reverse_freq)
    for i in range(num_reverse):
        pre_edges = post_edges = len(net.edges())
        post_edges = pre_edges + 1
        while (pre_edges != post_edges):
            pre_edges = post_edges = len(net.edges())
            edge = rd.sample(net.edges(), 1)
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
        edge = rd.sample(net.edges(), 1)
        edge = edge[0]
        net[edge[0]][edge[1]]['sign'] = -1 * net[edge[0]][edge[1]]['sign']
        post_edges = len(net.edges())
        if (pre_edges != post_edges):   print("ERROR: mutn sign change has changed the number of edges!")


def num_mutations(mutn_freq):
    # note: mutation should be < 1 OR, if > 1, an INT
    if (mutn_freq < 1):
        if (rd.random() < mutn_freq):
            return 1
        else:
            return 0

    else:
        return rd.randint(0, mutn_freq)


def calc_tractability(net, node1, node2, pref_type, node_fitness_type):
    tract_score = None

    size = float(len(net.edges()))

    fit1 = net.node[node1]['fitness']
    fit2 = net.node[node2]['fitness']

    if (node_fitness_type==0):
        if (pref_type == 0):  # control, first selection is used
            tract_score= 1
        if (pref_type == 1):
            if (rd.random()<.5): tract_score = fit1/size
            else:                tract_score = fit2/size
        elif (pref_type == 5):
            tract_score = abs(fit1 - fit2) /size

    elif (node_fitness_type==1):
        if (pref_type == 0):  # control, first selection is used
            tract_score = 1
        if (pref_type == 1):
            if (rd.random() < .5):
                tract_score = fit1 / (size*size)
            else:
                tract_score = fit2 / (size*size)
        elif (pref_type == 5):
            tract_score = abs(fit1 - fit2) / (size*size)


    elif (node_fitness_type==2):

        if (pref_type == 0):  # control, first selection is used
            tract_score= 1
        if (pref_type == 1):
            if (rd.random()<.5): tract_score = fit1
            else:                tract_score = fit2
        elif (pref_type == 5):
            tract_score = abs(fit1 - fit2)
        else:
            print("ERROR IN MUTATION: unknown preferential attachment type.")

    print("tractable_mutate.calc_tract(): tract score = " + str(tract_score))

    return tract_score


