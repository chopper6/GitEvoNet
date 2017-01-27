import math
import random as rd


# from random import SystemRandom as rd

def mutate(configs, net):
    # mutation operations: rm edge, add edge, rewire an edge, change edge sign, reverse edge direction
    grow_freq = float(configs['grow_mutation_frequency'])
    shrink_freq = float(configs['shrink_mutation_frequency'])

    # --------- NET MUTATIONS ------------- #

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
    for i in range(num_shrink):
        node = rd.sample(net.nodes(), 1)
        node = node[0]
        net.remove_node(node)

    # --------- NODE MUTATIONS ------------- #

    nodes = net.nodes()
    for node in nodes:
        edges_check = net.out_edges(node) + net.in_edges(node)
        edges = net.edges(node)
        if (len(edges_check) != len(edges)): print("MUTATE ERR need to specify out + in edges")

        mutate_node(net, node, configs)



def mutate_node(net, node, configs):
    add_freq = float(configs['add_edge_mutation_frequency'])
    rm_freq = float(configs['remove_edge_mutation_frequency'])
    rewire_freq = float(configs['rewire_mutation_frequency'])
    sign_freq = float(configs['sign_mutation_frequency'])
    reverse_freq = float(configs['reverse_edge_mutation_frequency'])

    # preferential attchmt
    num_edges = float(len(net.edges(node)))
    add_freq *= num_edges
    rm_freq /= num_edges
    print("Mutate: w/ " + str(num_edges) + " add freq = " + str(add_freq) + ", while rm freq = " + str(rm_freq))

    # ADD EDGE
    num_add = num_mutations(add_freq)
    for i in range(num_add):
        pre_size = post_size = len(net.edges(node))
        while (pre_size == post_size):  # ensure that net adds
            node2 = rd.sample(net.nodes(), 1)
            node2 = node2[0]
            while (node2 == node):
                node2 = rd.sample(net.nodes(), 1)
                node2 = node2[0]
            sign = rd.randint(0, 1)
            if (sign == 0):     sign = -1
            net.add_edge(node, node2, sign=sign)  #this must be randomized if direction is relevant
            post_size = len(net.edges(node))

    # REMOVE EDGE
    num_rm = num_mutations(rm_freq)
    for i in range(num_rm):
        edge = rd.sample(net.edges(node), 1)
        edge = edge[0]
        net.remove_edge(edge[0], edge[1])

    # REWIRE EDGE TODO: add this back
    '''
    num_rewire = num_mutations(rewire_freq)
    for i in range(num_rewire):
        pre_edges = post_edges = len(net.edges())
        post_edges = pre_edges + 1
        while (pre_edges != post_edges):  # ensure sucessful rewire
            edge = rd.sample(net.edges(), 1)
            edge = edge[0]
            sign = net[edge[0]][edge[1]]['sign']
            net.remove_edge(edge[0], edge[1])
            if (rd.random() < .5):
                node = edge[0]
            else:
                node = edge[1]
            node2 = node
            while (node2 == node):
                node2 = rd.sample(net.nodes(), 1)
                node2 = node2[0]
            if (rd.random() < .5):
                net.add_edge(node, node2, sign=sign)
            else:
                net.add_edge(node2, node, sign=sign)

            post_edges = len(net.edges())
            if (post_edges != pre_edges):
                net.add_edge(edge[0], edge[1], sign=sign)  # rewire failed, undo rm'd edge
                post_edges = len(net.edges())
                if (post_edges != pre_edges): print("MUTATION ERR: undo rm edge failed.")

    # REVERSE EDGE DIRECTION  TODO: add this back
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
    '''

    # CHANGE EDGE SIGN
    num_sign = num_mutations(sign_freq)
    for i in range(num_sign):
        pre_edges = len(net.edges(node))
        edge = rd.sample(net.edges(node), 1)
        edge = edge[0]
        net[edge[0]][edge[1]]['sign'] = -1 * net[edge[0]][edge[1]]['sign']
        post_edges = len(net.edges(node))
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


