#!/usr/bin/python3
import matplotlib
matplotlib.use('Agg') # This must be done before importing matplotlib.pyplot
import matplotlib.pyplot as plt
import networkx as nx
import os

def basic(population, dirr, iter, layout):
    #draws basic graph of most fit net
    #assumes already sorted by fitness

    plt.figure(figsize= (16,16))
    net = population[0].net
    num_edges = len(net.edges())

    posn = None

    if (layout == 'random'): posn = nx.random_layout(net)
    elif (layout == 'circular'): posn = nx.circular_layout(net)
    elif (layout == 'spring'): posn = nx.spring_layout(net)
    elif (layout == 'spectral'): posn = nx.spectral_layout(net)
    else: print("ERROR in draw(): unknown layout: " + str(layout))

    #color nodes by degree?
    node_degs = [len(net.out_edges(node)+net.in_edges(node)) for node in net.nodes()]
    node_degs_mult = [deg*20 for deg in node_degs]
    #should prob change multiplier to scale with net size


    file_name = dirr + "/draw/" + str(iter) + ".png"
    undir = net.to_undirected()
    edges = net.edges()
    colors = []
    for edge in edges:
        if (net[edge[0]][edge[1]]['sign']==-1): colors.append(0)
        elif (net[edge[0]][edge[1]]['sign']==1): colors.append(1)
        else: print("ERROR in draw(): unknown sign.")


    nx.draw_networkx_nodes(undir, pos=posn, node_size=node_degs_mult, node_color = node_degs, cmap=plt.get_cmap('plasma_r'), norm=matplotlib.colors.LogNorm(vmin=0, vmax=int(num_edges*.2)))
    nx.draw_networkx_edges(undir, pos=posn, edges=edges, edge_color=colors, edge_cmap=plt.get_cmap('plasma_r'))

    plt.savefig(file_name)
    plt.clf()
    plt.close()

def init(dirr):
    #merge with output.init() call?

    if not os.path.exists(dirr + "/draw/"):
        os.makedirs(dirr + "/draw/")
