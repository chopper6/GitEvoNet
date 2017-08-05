import math
import random as rd
import networkx as nx
import bias, util
# from random import SystemRandom as rd

def mutate(configs, net, gen_percent):
    # mutation operations: rm edge, add edge, rewire an edge, change edge sign, reverse edge direction
    rewire_freq = float(configs['rewire_mutation_frequency'])
    sign_freq = float(configs['sign_mutation_frequency'])
    grow_freq = float(configs['grow_mutation_frequency'])
    shrink_freq = float(configs['shrink_mutation_frequency'])

    mutn_type = str(configs['mutation_type'])

    # --------- MUTATIONS ------------- #

    # GROW (ADD NODE)
    num_grow = num_mutations(grow_freq, mutn_type, gen_percent)
    if (num_grow > 0): add_nodes(net, num_grow, configs)

    # SHRINK (REMOVE NODE)
    # poss outdated
    num_shrink = num_mutations(shrink_freq, mutn_type, gen_percent)
    if (num_shrink > 0): shrink(net, num_shrink, configs)

    # REWIRE EDGE
    num_rewire = num_mutations(rewire_freq, mutn_type, gen_percent)
    rewire(net, num_rewire, configs['biased'], configs['bias_on'], configs['output_directory'], configs)

    # CHANGE EDGE SIGN
    # poss outdated
    num_sign = num_mutations(sign_freq, mutn_type, gen_percent)
    if (num_sign > 0): change_edge_sign(net, num_sign)



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


def add_this_edge(net, configs, node1=None, node2=None, sign=None):

    biased = util.boool(configs['biased'])
    reverse_allowed = util.boool(configs['reverse_edges_allowed'])
    bias_on = configs['bias_on']

    if not sign:
        sign = rd.randint(0, 1)
        if (sign == 0): sign = -1

    pre_size = post_size = len(net.edges())
    i=0
    while (pre_size == post_size):  # ensure that net adds

        if not node1:
            node = rd.sample(net.nodes(), 1)
            node1 = node[0]

        if not node2:
            node2 = node1
            while (node2 == node1):
                node2 = rd.sample(net.nodes(), 1)
                node2 = node2[0]

        if reverse_allowed:
            if not net.has_edge(node1, node2):
                net.add_edge(node1, node2, sign=sign)
                post_size = len(net.edges())
        else:
            if not net.has_edge(node1, node2) and not net.has_edge(node2, node1):
                net.add_edge(node1, node2, sign=sign)
                post_size = len(net.edges())

        i+=1
        if (i == 10000000): util.cluster_print(configs['output_directory'], "WARNING mutate.add_this_edge() is looping a lot.\n")

    if (biased == True and bias_on == 'edges'): bias.assign_an_edge_consv(net, [node1,node2], configs['bias_distribution'])




def add_edges(net, num_add, configs):

    if (num_add == 0): print("WARNING in mutate(): 0 nodes added in add_nodes\n")

    for j in range(num_add):
        add_this_edge(net, configs)


def add_nodes(net, num_add, configs):

    edge_node_ratio = float(configs['edge_to_node_ratio'])
    biased = util.boool(configs['biased'])

    # ADD NODE
    for i in range(num_add):
        pre_size = post_size = len(net.nodes())
        while (pre_size == post_size):
            new_node = rd.randint(0, len(net.nodes()) * 1000)  # hope to hit number that doesn't already exist
            if new_node not in net.nodes():
                net.add_node(new_node)
                post_size = len(net.nodes())
        if (biased == True and configs['bias_on'] == 'nodes'): bias.assign_a_node_consv(net, new_node,configs['bias_distribution'])

        # ADD EDGE TO NEW NODE TO KEEP CONNECTED
        add_this_edge(net, configs)

    # MAINTAIN NODE_EDGE RATIO
    # ASSUMES BTWN 1 & 2
    num_edge_add = 0
    curr_ratio = (len(net.edges()) + num_edge_add) / float(len(net.nodes()))
    while (curr_ratio < edge_node_ratio):
        curr_ratio = (len(net.edges()) + num_edge_add) / float(len(net.nodes()))
        num_edge_add += 1
    add_edges(net, num_edge_add, configs)

def rm_edges(net, num_rm, configs):
    # constraints: doesn't leave 0 deg edges or mult connected components

    for j in range(num_rm):
        pre_size = post_size = len(net.edges())
        i=0
        while (pre_size == post_size):
            edge = rd.sample(net.edges(), 1)
            edge = edge[0]

            # don't allow 0 deg edges
            while ((net.in_degree(edge[0]) + net.out_degree(edge[0]) == 1) or (net.in_degree(edge[1]) + net.out_degree(edge[1]) == 1)):
                edge = rd.sample(net.edges(), 1)
                edge = edge[0]

            sign_orig = net[edge[0]][edge[1]]['sign']
            net.remove_edge(edge[0], edge[1])

            ensure_single_cc(net, configs, node1=edge[0], node2=edge[1], sign_orig=sign_orig)

            post_size = len(net.edges())
            i+=1

            if (i==10000000): util.cluster_print(configs['output_directory'], "WARNING mutate.rm_edges() is looping a lot.\n")


def ensure_single_cc(net, configs, node1=None, node2=None, sign_orig=None):
    #rewires [node1, node2] at the expense of a random, non deg1 edge

    net_undir = net.to_undirected()
    num_cc = nx.number_connected_components(net_undir)

    if (num_cc != 1): #rm_edge() will recursively check
        if not node1:
            components = list(nx.connected_components(net_undir))
            c1 = components[0]
            node1 = rd.sample(c1, 1)
            node1 = node1[0]

        if not node2:
            components = list(nx.connected_components(net_undir))
            c2 = components[1]
            node2 = rd.sample(c2, 1)
            node2 = node2[0]

        if not sign_orig:
            sign_orig = rd.randint(0, 1)
            if (sign_orig == 0): sign_orig = -1

        add_this_edge(net, configs, node1=node1, node2=node2, sign=sign_orig)
        rm_edges(net, 1, configs) #calls ensure_single_cc() at end

    #one last check (redundant)
    net_undir = net.to_undirected()
    num_cc = nx.number_connected_components(net_undir)
    assert (num_cc > 1)

def rewire(net, num_rewire, bias, bias_on, dirr, configs):
    # constraints: no 0 deg nodes, 1 connected component
    # avoid: re-adding a node/edge that already exists
    bias = util.boool(bias)

    net_undir = net.to_undirected()
    num_cc = nx.number_connected_components(net_undir)
    assert (num_cc == 1)

    for i in range(num_rewire):

        # poss, but unlikely
        add_this_edge(net, configs)
        rm_edges(net,1,configs)


def rewire_componentsOK(net, num_rewire):
    #obselete i think
    assert(False)

    print("\nWhy am i in mutate.rewire_componentsOK???\n")

    for i in range(num_rewire):
        # print("rewire(): before.")
        pre_edges = len(net.edges())
        rewire_success = False

        while (rewire_success == False):  # ensure sucessful rewire
            edge = rd.sample(net.edges(), 1)
            edge = edge[0]
            sign_orig = net[edge[0]][edge[1]]['sign']

            node = rd.sample(net.nodes(), 1)
            node = node[0]
            node2 = node
            while (node2 == node):
                node2 = rd.sample(net.nodes(), 1)
                node2 = node2[0]
            sign = rd.randint(0, 1)
            if (sign == 0):     sign = -1

            net.add_edge(node, node2, sign=sign)
            #else: net.add_edge(node2, node, sign=sign)
            post_edges = len(net.edges())
            if (post_edges > pre_edges):  # check that edge successfully added
                net.remove_edge(edge[0], edge[1])

                post_edges = len(net.edges())
                if (post_edges == pre_edges):  # check that edge successfully removed
                    rewire_success = True
                else:
                    print("ERROR IN REWIRE: num edges not kept constant")
                    return


def shrink(net, num_shrink, configs):
    pre_size = len(net.nodes())
    for i in range(num_shrink):
        assert(False) #should use SHRINK w/o revising

        #REMOVE NODE
        node = rd.sample(net.nodes(), 1)
        node = node[0]

        num_edges_lost = len(net.in_edges(node)+net.out_edges(node)) #ASSUmeS directional reduction
        change_in_edges = 2-num_edges_lost

        net.remove_node(node)
        post_size = len(net.nodes())
        if (pre_size == post_size): print("MUTATE SHRINK() ERR: node not removed.")

        # MAINTAIN NODE:EDGE RATIO
        if (change_in_edges > 0): rm_edges(net,change_in_edges, configs)
        else: add_edges(net, -1*change_in_edges, configs)


def change_edge_sign(net, num_sign):
    for i in range(num_sign):
        pre_edges = len(net.edges())
        post_edges = pre_edges + 1
        while (pre_edges != post_edges):
            edge = rd.sample(net.edges(), 1)
            edge = edge[0]
            net[edge[0]][edge[1]]['sign'] = -1 * net[edge[0]][edge[1]]['sign']
            post_edges = len(net.edges())
            if (post_edges != pre_edges): print("ERROR IN SIGN CHANGE: num edges not kept constant.")

