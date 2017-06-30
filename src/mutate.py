import math
import random as rd
import networkx as nx
import net_generator
# from random import SystemRandom as rd

def mutate(configs, net, gen_percent, edge_node_ratio):
    # mutation operations: rm edge, add edge, rewire an edge, change edge sign, reverse edge direction
    rewire_freq = float(configs['rewire_mutation_frequency'])
    sign_freq = float(configs['sign_mutation_frequency'])
    grow_freq = float(configs['grow_mutation_frequency'])
    shrink_freq = float(configs['shrink_mutation_frequency'])

    mutn_type = str(configs['mutation_type'])

    # --------- MUTATIONS ------------- #
    # GROW (ADD NODE)
    # starts unconnected
    num_grow = num_mutations(grow_freq, mutn_type, gen_percent)
    if (num_grow > 0): add_nodes(net, num_grow, edge_node_ratio, configs)


    # SHRINK (REMOVE NODE)
    num_shrink = num_mutations(shrink_freq, mutn_type, gen_percent)
    pre_size = len(net.nodes())
    for i in range(num_shrink):

        #REMOVE NODE
        node = rd.sample(net.nodes(), 1)
        node = node[0]

        num_edges_lost = len(net.in_edges(node)+net.out_edges(node)) #ASSUmeS directional reduction
        change_in_edges = 2-num_edges_lost

        net.remove_node(node)
        post_size = len(net.nodes())
        if (pre_size == post_size): print("MUTATE SHRINK() ERR: node not removed.")

        # MAINTAIN NODE:EDGE RATIO
        if (change_in_edges > 0): rm_edges(net,change_in_edges)
        else: add_edges(net, -1*change_in_edges, configs)


    # REWIRE EDGE
    # TODO: try changing to rm, then add
    num_rewire = num_mutations(rewire_freq, mutn_type, gen_percent)
    rewire(net, num_rewire, configs['biased'], configs['bias_on'])


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



def add_edges(net, num_add, configs):

    for j in range(num_add):
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

        if (configs['biased'] == True and configs['bias_on'] == 'edges'): net_generator.assign_an_edge_consv(net, [node,node2], configs['bias_distribution'])


def add_nodes(net, num_add, edge_node_ratio, configs):
    # ADD NODE
    for i in range(num_add):
        pre_size = post_size = len(net.nodes())
        while (pre_size == post_size):
            node_num = rd.randint(0, len(net.nodes()) * 100)  # hope to hit number that doesn't already exist
            net.add_node(node_num)
            post_size = len(net.nodes())
        if (configs['biased'] == True and configs['bias_on'] == 'nodes'): net_generator.assign_a_node_consv(net, node_num,configs['bias_distribution'])

    if (num_add == 0): print("WARNING in mutate(): 0 nodes added in add_nodes\n")

    # ADD EDGE TO NEW NODE TO KEEP CONNECTED
    pre_size = post_size = len(net.edges())
    while (pre_size == post_size):  # ensure that net adds
        node2 = node = node_num
        while (node2 == node):
            node2 = rd.sample(net.nodes(), 1)
            node2 = node2[0]

        sign = rd.randint(0, 1)
        if (sign == 0):     sign = -1
        if (rd.random() < .5):
            net.add_edge(node, node2, sign=sign)
            the_edge = [node,node2]
        else:
            net.add_edge(node2, node, sign=sign)
            the_edge = [node2,node]
        post_size = len(net.edges())

    if (configs['biased'] == True and configs['bias_on'] == 'edges'): net_generator.assign_an_edge_consv(net, the_edge ,configs['bias_distribution'])

    # MAINTAIN NODE_EDGE RATIO
    # ASSUMES BTWN 1 & 2
    num_edge_add = 0
    curr_ratio = len(net.edges())/float(len(net.nodes()))
    if (curr_ratio < edge_node_ratio): num_edge_add += 1
    #pr_second = edge_node_ratio -1
    #if (rd.random() < pr_second): num_edge_add += 1

    add_edges(net, num_edge_add, configs)

def rm_edges(net, num_rm):

    for j in range(num_rm):
        pre_size = post_size = len(net.edges())
        while (pre_size == post_size):
            edge = rd.sample(net.edges(), 1)
            edge = edge[0]
            sign_orig = net[edge[0]][edge[1]]['sign']
            net.remove_edge(edge[0], edge[1])
            post_size = len(net.edges())
            if (post_size == pre_size): print("WARNING: mutate remove edge failed, trying again.")

            net_undir = net.to_undirected()
            num_cc = nx.number_connected_components(net_undir)

            # UNDO RM:
            if (num_cc > 1):
                net.add_edge(edge[0], edge[1], sign=sign_orig)
                net_undir = net.to_undirected()
                num_cc = nx.number_connected_components(net_undir)
                post_size = len(net.edges())
                if (num_cc > 1 or post_size!=pre_size):
                    print("ERROR rewire(): undo failed to restore to single component")
                    return 1



def rewire(net, num_rewire, bias, bias_on):
    for i in range(num_rewire):
        # print("rewire(): before.")
        pre_edges = len(net.edges())
        rewire_success = False
        net_undir = net.to_undirected()
        num_cc = nx.number_connected_components(net_undir)
        if (num_cc > 1): print("mutation(): ERROR: multiple components!")

        while (rewire_success == False):  # ensure sucessful rewire
            edge = rd.sample(net.edges(), 1)
            edge = edge[0]

            # don't allow 0 deg edges
            while ((net.in_degree(edge[0]) + net.out_degree(edge[0]) == 1) or (net.in_degree(edge[0]) + net.out_degree(edge[0]) == 1)):
                edge = rd.sample(net.edges(), 1)
                edge = edge[0]

            sign_orig = net[edge[0]][edge[1]]['sign']
            if (bias == True and bias_on == 'edges'): consv_score = net[edge[0]][edge[1]]['conservation_score']

            node = rd.sample(net.nodes(), 1)
            node = node[0]
            node2 = node
            while (node2 == node):
                node2 = rd.sample(net.nodes(), 1)
                node2 = node2[0]
            sign = rd.randint(0, 1)
            if (sign == 0):     sign = -1

            if (bias == True and bias_on == 'edges'): net.add_edge(node, node2, sign=sign, conservation_score = consv_score)
            else:  net.add_edge(node, node2, sign=sign)
            #else: net.add_edge(node2, node, sign=sign)
            post_edges = len(net.edges())
            if (post_edges > pre_edges):  # check that edge successfully added
                net.remove_edge(edge[0], edge[1])
                net_undir = net.to_undirected()
                num_cc = nx.number_connected_components(net_undir)
                # print("rewire(): mid.")

                # UNDO REWIRE:
                if (num_cc > 1):
                    if (bias == True and bias_on == 'edges'): net.add_edge(edge[0], edge[1], sign=sign_orig, conservation_score = consv_score)
                    else: net.add_edge(edge[0], edge[1], sign=sign_orig)
                    net.remove_edge(node, node2)
                    post_edges = len(net.edges())
                    net_undir = net.to_undirected()
                    num_cc = nx.number_connected_components(net_undir)
                    if (num_cc > 1): 
                        print("ERROR rewire(): undo failed to restore to single component")
                        return 1
                    if (post_edges != pre_edges): print("\nMUTATE() ERROR: undo rewire failed.")
                else:
                    post_edges = len(net.edges())
                    if (post_edges == pre_edges):  # check that edge successfully removed
                        rewire_success = True
                    else:
                        print("ERROR IN REWIRE: num edges not kept constant")
                        return


def rewire_componentsOK(net, num_rewire):
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
