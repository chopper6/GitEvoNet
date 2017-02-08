#!/usr/bin/python3
import matplotlib
matplotlib.use('Agg') # This must be done before importing matplotlib.pyplot
import matplotlib.pyplot as plt
import networkx as nx

def basic(population, dirr, iter):
    #draws basic graph of most fit net
    #assumes already sorted by fitness

    file_name = dirr + "/draw/" + str(iter) + ".png"
    undir = population[0].net.to_undirected()
    nx.draw(undir)
    plt.savefig(file_name)


