#!/usr/bin/python3
import matplotlib
matplotlib.use('Agg') # This must be done before importing matplotlib.pyplot
import matplotlib.pyplot as plt
import networkx as nx
import os

def basic(population, dirr, iter):
    #draws basic graph of most fit net
    #assumes already sorted by fitness

    file_name = dirr + "/draw/" + str(iter) + ".png"
    undir = population[0].net.to_undirected()
    nx.draw(undir, node_size=10)
    plt.savefig(file_name)
    plt.clf()

def init(dirr):
    #merge with output.init() call?

    if not os.path.exists(dirr + "/draw/"):
        os.makedirs(dirr + "/draw/")
