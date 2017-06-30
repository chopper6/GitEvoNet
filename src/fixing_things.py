import matplotlib
matplotlib.use('Agg') # you need this line if you're running this code on rupert
import sys, os, matplotlib.pyplot as plt, matplotlib.patches as mpatches, networkx as nx, numpy as np
import math
#from scipy.stats import itemfreq
import matplotlib.ticker as ticker
import matplotlib.font_manager as font_manager
from matplotlib import rcParams
import random as rd


def plot_em(gen_0_file, gen_end_file):
    #update_rcParams()
    # each line in 'input.txt' should be: [network name (spaces allowed) followed by /path/to/edge/file.txt/or/pickled/network.dump]

    gen_0 = nx.read_edgelist(gen_0_file, nodetype=int, create_using=nx.DiGraph())
    gen_end = nx.read_edgelist(gen_end_file, nodetype=int, create_using=nx.DiGraph())

    colors = ['#ff5050', '#6699ff']
    titles = ['Generation 1', 'Generation 2000']
    markers = ['D', '.']
    nets = [gen_0, gen_end]

    H = []
    #loglog
    for  i in range(2): # gen_0 scatter, gen_end scatter, gen_0 log, gen_end_log

        degrees = list(nets[i].degree().values())
        degs, freqs = np.unique(degrees, return_counts=True)
        tot = float(sum(freqs))
        freqs = [(f/tot)*100 for f in freqs]

        plt.loglog(degs, freqs, basex=10, basey=10, linestyle='',  linewidth=2, color = colors[i], alpha=1, markersize=8, marker=markers[i], markeredgecolor='None', )

        patch =  mpatches.Patch(color=colors[i], label=titles[i])
        H = H + [patch]
        i+=1

    #FORMAT PLOT
    ax = plt.gca() # gca = get current axes instance

    ax.set_xlim([0,16])
    ax.set_ylim([0,200])

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tick_params(axis='both', which='both', right='off', top='off') #http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.tick_params
    plt.legend(loc='upper right', handles=H, frameon=False,fontsize= 11)
    plt.xlabel('Degree')
    plt.ylabel('Number of Nodes with Given Degree')
    #plt.title('Degree Distribution of ' + str(title) + ' vs Simulation')

    plt.tight_layout()
    plt.savefig("loglog.png", dpi=300,bbox='tight') # http://matplotlib.org/api/figure_api.html#matplotlib.figure.Figure.savefig
    plt.clf()
    plt.cla()
    plt.close()


    H = []
    #scatter

    for  i in range(2): # gen_0 scatter, gen_end scatter, gen_0 log, gen_end_log

        degrees = list(nets[i].degree().values())
        degs, freqs = np.unique(degrees, return_counts=True)
        tot = float(sum(freqs))
        freqs = [(f/tot)*100 for f in freqs]

        s = [10 for n in range(len(degs))]
        plt.scatter(degs, freqs, color = colors[i], alpha=1, s=s, marker=markers[i])

        patch =  mpatches.Patch(color=colors[i], label=titles[i])
        H = H + [patch]
        i += 1

    #FORMAT PLOT
    ax = plt.gca() # gca = get current axes instance

    #ax.set_xscale('log')
    #ax.set_yscale('log')
    ax.set_xlim([0,16])
    ax.set_ylim([0,200])

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tick_params(axis='both', which='both', right='off', top='off') #http://matplotlib.org/api/axes_api.html#matplotlib.axes.Axes.tick_params
    plt.legend(loc='upper right', handles=H, frameon=False,fontsize= 11)
    plt.xlabel('Degree')
    plt.ylabel('Number of Nodes with Given Degree')
    #plt.title('Degree Distribution of ' + str(title) + ' vs Simulation')

    plt.tight_layout()
    plt.savefig("scatter.png", dpi=300,bbox='tight') # http://matplotlib.org/api/figure_api.html#matplotlib.figure.Figure.savefig
    plt.clf()
    plt.cla()
    plt.close()




if __name__ == "__main__":
    base_dir = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/data/output/conf2/" #customize for curr work
    real_net_file = "/home/2014/choppe1/Documents/EvoNet/virt_workspace/data/input/input_all_nets.txt" #check this is still on yamaska

    print("plotting " + sys.argv[1] + " and " + sys.argv[2])
    plot_em(sys.argv[1], sys.argv[2])

    print("\nDone.\n")
